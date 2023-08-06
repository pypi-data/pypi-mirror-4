import re, simplejson

def mako_preprocessor(text):
  text = re.sub('<mako:', "<%", text)
  text = re.sub('</mako:', "</%", text)
  return text
  
  
def json(text):
  print type(text)
  return text