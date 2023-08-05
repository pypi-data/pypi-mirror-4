import os, tg
from paste.urlparser import StaticURLParser
from webob.exc import HTTPFound
from limits import ModernBrowserLimit, BasicBrowserLimit, MinimalBrowserLimit, HTML5BrowserLimit
import public

limits = {'MODERN':ModernBrowserLimit,
          'HTML5':HTML5BrowserLimit,
          'BASIC':BasicBrowserLimit,
          'MINIMAL':MinimalBrowserLimit}

class BrowserVersionMiddleware(object):
    def __init__(self, application):
        self.limits = {}
        self.limits.update(limits)
        self.limits.update(tg.config.get('browserlimits', {}))

        self.limit_browsers = tg.config.get('browserlimit', 'BASIC')
        self.limit = self.limits[self.limit_browsers]
        self.application = application

        self.public_path = os.path.dirname(public.__file__)
        self.statics = StaticURLParser(self.public_path)

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if path_info.startswith('/_browserlimit/'):
            path_info = path_info[len('/_browserlimit/'):]
            environ['PATH_INFO'] = path_info
            return self.statics(environ, start_response)

        user_agent = environ.get('HTTP_USER_AGENT')
        if self.limit(user_agent).is_met(environ):
            return self.application(environ, start_response)
        else:
            return HTTPFound(location='/_browserlimit/unsupported.html')(environ, start_response)
