from webob import Request


class SecureCookiesMiddleware(object):
    """
    This middleware intercepts non-https requests and strips all Set-Cookie
    headers for cookies which are secure.

    Note that this will ONLY work given the following conditions (which are
    true in the typical beaker/pylons/webob environment:
        * the 'secure' attribute comes at the end of the cookie
        * each cookie gets it's own Set-Cookie header
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)
        resp = req.get_response(self.app)
        if req.scheme == 'http':
            # Strip all secure cookies.
            if 'Set-Cookie' in resp.headers:
                for header in resp.headers.getall('Set-Cookie'):
                    if header.endswith('secure'):
                        name = header.split('=')[0].strip()
                        resp.unset_cookie(name)
        return resp(environ, start_response)
