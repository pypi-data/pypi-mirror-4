from webob import Request
from webob.exc import HTTPTemporaryRedirect


class PruneCookiesMiddleware(object):
    """
    Prune cookies with either a blacklist or a whitelist. If a blacklist is
    provided, delete all cookies from the client which have keys that match the
    sequence provided. If a whitelist is provided, delete all cookies which
    have keys that do not match the sequence provided.
    """
    def __init__(self, app, whitelist=None, blacklist=None):
        self.app = app
        assert (whitelist is None) ^ (blacklist is None), \
            "whitelist or blacklist is required, but not both"
        self.whitelist = whitelist
        self.blacklist = blacklist

    def __call__(self, environ, start_response):
        req = Request(environ)

        to_delete = set()
        for cookie in req.cookies:
            if ((self.whitelist and (cookie not in self.whitelist)) or
                    (self.blacklist and (cookie in self.blacklist))):
                to_delete.add(cookie)

        if to_delete:
            resp = HTTPTemporaryRedirect(location=req.url)
            for cookie in to_delete:
                resp.delete_cookie(cookie)
        else:
            resp = req.get_response(self.app)

        return resp(environ, start_response)
