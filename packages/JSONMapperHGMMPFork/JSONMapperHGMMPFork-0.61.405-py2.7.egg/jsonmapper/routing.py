from operator import attrgetter

STANDARD_FORM_ATTRS = [{'attr' :"GET", 'request_method' : "GET"}, {'attr' :"POST", 'request_method' : "POST"}]
JSON_FORM_ATTRS = [{'attr' :"GET", 'request_method' : "GET"}, {'attr' :"POST", 'request_method' : "POST", 'xhr' : False}, {'attr' :"ajax", 'request_method' : "POST", 'xhr' : True, 'renderer':"json"}]
JSON_LINK_ATTRS = [{'attr' :"GET", 'request_method' : "GET"}, {'attr' :"ajax", 'request_method' : "POST", 'xhr' : True, 'renderer':"json"}]


class App(object):
    def __init__(self, name):
        self.name = name



class FunctionRoute(object):
    def __init__(self, name, path_exp, factory, view, renderer, route_attrs = {}):
        self.name = name
        self.path_exp = path_exp
        self.factory = factory
        self.view = view
        self.renderer = renderer
        self.route_attrs = route_attrs

    def getRouteName(self, app_name):
        return '{}_{}'.format(app_name, self.name)

    def setup(self, apps, config):
        for app in apps:
            route_name =self.getRouteName(app.name)
            config.add_route(route_name, self.path_exp, factory = self.factory, **self.route_attrs)
            self.addView(config, route_name)
    def addView(self, config, route_name):
        config.add_view(self.view, route_name = route_name, renderer = self.renderer)

class ClassRoute(FunctionRoute):
    def __init__(self, name, path_exp, factory, view, renderer = None, view_attrs = []):
        self.view_attrs = view_attrs
        super(ClassRoute, self).__init__(name, path_exp, factory, view, renderer)
    def addView(self, config, route_name):
        for attrs in self.view_attrs:
            renderer = attrs.pop("renderer", self.renderer)
            config.add_view(view = self.view, route_name = route_name, renderer = renderer, **attrs)
