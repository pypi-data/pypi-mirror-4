&#127864; Mai Tai - Handy WSGI Utilities
============================================

Scott Torborg - [Cart Logic](http://www.cartlogic.com)

Mai Tai is a collection of useful WSGI middlewares. The goal is to stand
alongside the excellent [Paste](http://pythonpaste.org) and
[WebOb](http://webob.org) libraries and provide tools that are handy for
practical WSGI application administration.

It is also:

* 40 mL white rum
* 20 mL dark rum
* 15 mL orange curacao
* 15 mL Orgeat syrup
* 10 mL fresh lime juice
* spear and lime peel garnish

Installation
============

    $ pip install maitai


Included
========

### ``GitSHAMiddleware`` ###

Tag requests with the current SHA1 hash of 1 or more git repositories.

    from maitai.gitsha import GitSHAMiddleware

    app = SuperAwesomeApp()
    app = GitSHAMiddlware(app, '/opt/superawesome')

Inside your app code, you can access the SHA1 like:

    version = environ['git-sha1.superawesome']


### ``SecureCookiesMiddleware`` ###

Intercept non-https requests and strip any ``Set-Cookie`` headers which set
cookies that are secure.

Useful for working around other misbehaving components which are leaking data
in your hybrid http/https deployment.

    from maitai.securecookies import SecureCookiesMiddleware

    app = SlightlyLeakyStack()
    app = SecureCookiesMiddleware(app)


### ``RenameCookieMiddleware`` ###

Look for a cookie by a certain name on the client, if it is present, rename it
to a new name and reset metadata to desired values.

    from maitai.renamecookie import RenameCookieMiddleware

    app = App()
    app = RenameCookieMiddleware(app, 'old_cookie', 'new_cookie', secure=True)

This works by issuing an immediate 307 redirect in response to any requests
that have a cookie which matches 'old_cookie'.

Additional keyword arguments are available for setting all cookie metadata
attributes supported by WebOb's ``response.set_cookie()`` call, including
``expires``, ``max_age``, ``secure``, ``domain``, ``path``, ``httponly``, and
``comment``.


### ``PruneCookiesMiddleware`` ###

Prune all cookies from the client that either match a blacklist, or don't match
a whitelist.

    from maitai.prunecookies import PruneCookieMiddleware

    app = App()
    app = PruneCookiesMiddleware(app, whitelist=('session_id',
                                                 '__utma', '__utmb',
                                                 '__utmc', '__utmz'))

**Note:** As indicated above, regardless of your server-side code, don't forget
that you may have 3rd-party javascript like Google Analytics which uses
specific cookie names. Don't throw away your data!

This works by issuing an immediate 307 redirect in response to any requests
that have a cookie that is "to be discarded".


### ``StatusCodeRedirect`` ###

Internally redirect a request based on status code. If a response has an HTTP
status which matches the list configured in the middleware, the request is
re-run with the URL path set to the configured path.

Inspired by the middleware that was included in Pylons, and shares the same
semantics, but rewritten for simplicity and to use WebOb.

    from maitai.statuscode import StatusCodeRedirect

    app = SuperAwesomeApp()
    app = StatusCodeRedirect(app, errors=(400, 401, 403, 404, 500),
                             path='/error_handler')

Request re-issuing is non-recursive: the output of the second request will be
used no matter what it is.


To Do
=====

Additional tools that may be coming soon:

- Logging utilities.
- Request latency timing by request type.


License
=======

Mai Tai is licensed under an MIT license. Please see the LICENSE file for more
information.


Code Standards
==============

Mai Tai has a comprehensive test suite with 100% line and branch coverage, as
reported by the excellent ``coverage`` module. To run the tests, simply run in
the top level of the repo:

    $ nosetests

There are no [PEP8](http://www.python.org/dev/peps/pep-0008/) or
[Pyflakes](http://pypi.python.org/pypi/pyflakes) warnings in the codebase. To
verify that:

    $ pip install pep8 pyflakes
    $ pep8 .
    $ pyflakes .

Any pull requests must maintain the sanctity of these three pillars.
