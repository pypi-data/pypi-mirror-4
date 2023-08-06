from collections import defaultdict as ddict
from haml import preprocessor as haml_preprocessor
from random import randint
from types import ClassType
import inspect
import mako.lookup
import web

urls = []
handlers = ddict(lambda: ClassType("",(),{}))

class method(object):
    def __init__(self, method, url):
        self.method = method
        self.url = url
        self.handler = handlers[url]
    def __call__(self, func):
        def get_response(self, *args, **kwargs):
            response = func(*args, **kwargs) or haml(func.__name__)
            return response
        self.handler.__dict__[self.method] = get_response
        urls.append(self.url)
        urls.append(self.handler)

class get(method):
    def __init__(self, url):
        super(get, self).__init__("GET", url)

class post(method):
    def __init__(self, url):
        super(post, self).__init__("POST", url)

def run():
    from sys import argv
    if not argv[0].endswith("dev_server.py"):
        web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    web.application(urls).run()

haml_lookup = mako.lookup.TemplateLookup(directories=["views"], preprocessor=haml_preprocessor)

def haml(name = None, **template_vars):
    print template_vars
    caller_frame = inspect.currentframe().f_back
    name = (name or caller_frame.f_code.co_name)
    template_vars = template_vars or caller_frame.f_locals
    template_vars.pop('self', None)
    return haml_lookup.get_template(name + ".haml").render(**template_vars)
