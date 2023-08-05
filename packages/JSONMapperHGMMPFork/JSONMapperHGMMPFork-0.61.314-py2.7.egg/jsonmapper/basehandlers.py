from formencode.variabledecode import variable_decode
from formencode.validators import Invalid
from pyramid.httpexceptions import HTTPNotImplemented, HTTPUnauthorized, HTTPFound
from pyramid.view import view_config
from BeautifulSoup import BeautifulSoup
import formencode
from datetime import datetime
from babel.numbers import parse_decimal, format_decimal, NumberFormatError

import logging
log = logging.getLogger(__name__)

class InvalidCSRFToken(Exception):pass


class BaseHandler(object):
  def __init__(self, context, request):
      self.request = request
      self.context = context


_ = lambda s: s


class FormHeading(object):
  def __init__(self, html_label, tag = 'legend', classes = ''):
    self.html_label = html_label
    self.tag = tag
    self.classes = classes



class SanitizedHTMLString(formencode.validators.String):
  messages = {"invalid_format":'There was some error in your HTML!'}
  valid_tags = ['a','strong', 'em', 'p', 'ul', 'ol', 'li', 'br', 'b', 'i', 'u', 's', 'strike', 'font', 'pre', 'blockquote', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
  valid_attrs = ['size', 'color', 'face', 'title', 'align', "style"]
  def sanitize_html(self, html):
      soup = BeautifulSoup(html)
      for tag in soup.findAll(True):
          if tag.name.lower() not in self.valid_tags:
              tag.extract()
          elif tag.name.lower() != "a":
              tag.attrs = [attr for attr in tag.attrs if attr[0].lower() in self.valid_attrs]
          else:
              attrs = dict(tag.attrs)
              tag.attrs = [('href', attrs.get('href')), ('target', '_blank')]
      val = soup.renderContents()
      return val.decode("utf-8")
  def _to_python(self, value, state):
    value = super(self.__class__, self)._to_python(value, state)
    try:
      return self.sanitize_html(value)
    except Exception, e:
      log.error("HTML_SANITIZING_ERROR %s", value)
      raise formencode.Invalid(self.message("invalid_format", state, value = value), value, state)

class OneOfState(formencode.validators.OneOf):
    isChoice = True
    list = None
    stateKey = None
    testValueList = False
    hideList = False
    getValue = None
    getKey = None
    custom_attribute = 'custom'
    __unpackargs__ = ('list',)

    def getValues(self, request):
      obj = request
      for key in self.stateKey.split("."): obj = getattr(obj, key)
      return map(self.getValue, obj)
    def getKeys(self, request):
      obj = request
      for key in self.stateKey.split("."): obj = getattr(obj, key)
      return map(self.getKey, obj)
    def getItems(self, request):
      obj = request
      for key in self.stateKey.split("."): obj = getattr(obj, key)
      return obj
    def hasCustom(self, request):
      return len(filter(None, map(lambda item: getattr(item, self.custom_attribute, False),self.getItems(request)))) > 0

    def keyToPython(self, value, state = None):
        return value

    def customValueToPython(self, value, state = None):
        return value

    def _to_python(self, value, state):
        if isinstance(value, dict):
          custom = self.customValueToPython(value.get("custom", None), state)
          val = self.keyToPython(value.get("value", None), state)
          items = {self.getKey(s):getattr(s, self.custom_attribute, False) for s in self.getItems(state)}
          is_custom = items.get(val, False)
        else:
          is_custom = False
          val = self.keyToPython(value, state)
        self.list = self.getKeys(state)
        if not val in self.list:
            if self.hideList:
                raise Invalid(self.message('invalid', state), val, state)
            else:
                try:
                    items = '; '.join(map(str, self.list))
                except UnicodeError:
                    items = '; '.join(map(unicode, self.list))
                raise Invalid(
                    self.message('notIn', state,
                        items=items, val=val), val, state)
        else:
            # breaking change: this was
            # return custom if is_custom and custom else val

          return custom if is_custom else val

    validate_python = formencode.FancyValidator._validate_noop
class OneOfStateNoCustom(OneOfState):
    def hasCustom(self, req):
        return False

class OneOfStateInt(OneOfState):
    def keyToPython(self, value, state):
        if value is None: return None
        try:
            return int(value)
        except:
            raise Invalid(self.message('invalid', state), val, state)


class DateValidator(formencode.FancyValidator):
  messages = dict(
        badFormat=_('Please enter the date in the form %(format)s'),
        monthRange=_('Please enter a month from 1 to 12'),
        invalidDay=_('Please enter a valid day'),
        dayRange=_('That month only has %(days)i days'),
        invalidDate=_('That is not a valid day (%(exception)s)'),
        unknownMonthName=_('Unknown month name: %(month)s'),
        invalidYear=_('Please enter a number for the year'),
        fourDigitYear=_('Please enter a four-digit year after 1899'),
        wrongFormat=_('Please enter the date in the form %(format)s')
    )
  def _to_python(self, value, state):
    try:
      value = datetime.strptime(value, self.format)
    except ValueError, e:
      raise formencode.Invalid(self.message("badFormat", state, format = self.format.replace('%d', 'dd').replace('%m', 'mm').replace('%Y', 'yyyy'), value=value), value, state)
    else: return value
      
class DecimalValidator(formencode.FancyValidator):
  messages = {"invalid_amount":_('Bitte eine Zahl eingeben'),
        "amount_too_high":_("Bitte eine Zahl %(max_amount)s oder kleiner eingeben"),
        "amount_too_low":_("Bitte eine Zahl %(min_amount)s oder größer eingeben")
      }
  max = None
  min = None
  def _to_python(self, value, state):
    if not getattr(self, 'required', False) and not value:
        return getattr(self, 'if_missing', None)
    try:
      value = parse_decimal(value, locale = state._LOCALE_)
      if self.max and value > self.max:
        raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_decimal(self.max, locale=state._LOCALE_)), value, state)
      if self.min and value < self.min:
        raise formencode.Invalid(self.message("amount_too_low", state, min_amount = format_decimal(self.min, locale=state._LOCALE_)), value, state)
    except NumberFormatError, e:
      raise formencode.Invalid(self.message("invalid_amount", state, value = value), value, state)
    except ValueError, e:
      raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_decimal(self.max, locale=state._LOCALE_)), value, state)
    else: return value
      

class FullValidatedFormHandler(object):
  def __init__(self, context = None, request = None):
      self.request = request
      self.context = context
      self.result = {'values':{}, 'errors':{}, 'schemas' : self.schemas, 'formencode':formencode}
      ### generate groups error/value groups for each schema
      self.result['values'].update([(k,{}) for k in self.schemas.keys()])
      self.result['errors'].update([(k,{}) for k in self.schemas.keys()])

  @view_config(request_method='GET')
  def GET(self):
    self.request.session.get_csrf_token()
    add_globals = getattr(self, "add_globals", None)
    if(add_globals is not None):
      self.result = add_globals(self.request, self.result)
    pre_fill_values = getattr(self, "pre_fill_values", None)
    if(pre_fill_values is not None):
      self.result = pre_fill_values(self.request, self.result)
    return self.result

  @view_config(request_method='POST')
  def POST(self):
    try:
        return self.validate_form()
    except InvalidCSRFToken:
        add_globals = getattr(self, "add_globals", None)
        if(add_globals is not None):
            self.result = add_globals(self.request, self.result)
        return self.result

  def validate_form(self):
    values = variable_decode(self.request.params)
    schema_id = values['type']
    try:
        resp = self.validate_values(values)
    except Invalid, error:
      log.error(error.error_dict)
      self.result['values'][schema_id] = error.value or {}
      self.result['errors'][schema_id] = error.error_dict or {}
      self.request.response.status_int = 401
    else:
      ### if validate_values/on_success returns anything else than a redirect, it must be some validation error
      self.result['values'][schema_id] = resp['values']
      self.result['errors'][schema_id] = resp['errors']
      self.request.response.status_int = 401
    add_globals = getattr(self, "add_globals", None)
    if(add_globals is not None):
      self.result = add_globals(self.request, self.result)
    return self.result


  def validate_json(self,renderTemplates = {}):
    values = self.request.json_body
    schema_id = values['type']

    def wrap_errors(errors):
        map = {}
        map[schema_id] = errors
        return formencode.variabledecode.variable_encode(map)

    try:
        form_result = self.validate_values(values)
    except Invalid, error:
        return {'success': False, 'values':error.value or {}, 'errors':wrap_errors(error.unpack_errors())}
    except HTTPFound, e: # success case
        return {'redirect': e.location}
    except InvalidCSRFToken:
        return {'success':False, 'errorMessage':_("An error occured, please try again.")}
    else:
        form_result.setdefault('success', False)
        form_result['errors'] = wrap_errors(form_result.get('errors', {}))
        return form_result


  def validate_values(self, values, renderTemplates = {}):
        req = self.request
        if values.get('token') != req.session.get_csrf_token():
            raise InvalidCSRFToken()
        try:
            ### determine actual form used in this submission
            schema_id = values['type']
            schema = self.schemas[schema_id]()
        except KeyError, e:
            raise HTTPNotImplemented("Unexpected submission type!")
        else:
            form_result = schema.to_python(values.get(schema_id), state=self.request)
            return schema.on_success(self.request, form_result)