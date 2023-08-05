from webob import Request


class StatusCodeRedirect(object):
    """
    Internally redirects a request based on status code.

    StatusCodeRedirect watches the response of the app it wraps. If the
    response is an error code in the errors sequence passed the request
    will be re-run with the path URL set to the path passed in

    This operation is non-recursive and the output of the second
    request will be used no matter what it is.

    Rewritten from Pylons version, but shares the same semantics.
    """
    def __init__(self, app, errors=(400, 401, 403, 404),
                 path='/error/document'):
        """
        :param errors:
          A sequence (list, tuple) of error code integers that should be
          caught.
        :param path:
          The path to set for the next request down to the application.
        """
        self.app = app
        self.error_path = path
        self.errors = errors

    def __call__(self, environ, start_response):
        req = Request(environ)
        resp = req.get_response(self.app, catch_exc_info=True)

        if resp.status_int in self.errors:
            new_environ = environ.copy()
            new_environ.update({
                'statuscode.original_request': req,
                'statuscode.original_response': resp,
                'PATH_INFO': self.error_path,
            })
            new_req = Request(new_environ)
            new_resp = new_req.get_response(self.app, catch_exc_info=True)
            new_resp.status = resp.status
            resp = new_resp

        return resp(environ, start_response)
