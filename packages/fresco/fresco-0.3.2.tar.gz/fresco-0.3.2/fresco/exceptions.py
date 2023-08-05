__all__ = 'ResponseException', 'NotFound', 'NotFoundFinal', 'Unauthorized',\
          'Forbidden', 'BadRequest', 'Redirect', 'RedirectTemporary',\
          'RedirectPermanent'

from fresco.response import Response


class ResponseException(Exception):
    """\
    An exception class with an associated :class:`fresco.response.Response`
    instance that will render a suitable error page.
    """
    response = None

    #: If true, the error response will be returned immediately without trying
    #: any other routes.
    is_final = True


class NotFound(ResponseException):
    """\
    Raised when a view needs to signal a 404 not found condition.
    """
    response = Response.not_found()

    def __init__(self, final=False):
        """
        ``final`` is false by default, meaning other routes will be offered the
        opportunity to handle the request. Only after other routes have been
        tried will an error response be returned.
        """
        self.is_final = final


class BadRequest(ResponseException):
    """\
    Return a 400 Bad Request response
    """
    response = Response(['Bad request'], status=400)


class Unauthorized(ResponseException):
    """\
    Return a 401 Unauthorized response.

    Use this when you want to flag that the user does not have permission to
    access a resource but may be able to gain access, eg by logging in.
    """
    response = Response(['Unauthorized'], status=401)


class Forbidden(ResponseException):
    """\
    Return a 403 Forbidden response

    Use this when you want to flag that the user does not have permission to
    access a resource and that there is no possiblity to do so (eg they are
    already logged in, but their account does not have the right access
    permissions)
    """
    response = Response(['Forbidden'], status=403)


class RedirectTemporary(ResponseException):
    """\
    Return a 302 Found response. Example::

        raise RedirectTemporary('http://example.org/')
    """
    def __init__(self, *args, **kwargs):
        self.response = Response.redirect(*args, **kwargs)

Redirect = RedirectTemporary


class RedirectPermanent(ResponseException):
    """\
    Return a 301 Moved Permanently response. Example::

        raise RedirectPermanent('http://example.org/')

    """
    def __init__(self, *args, **kwargs):
        self.response = Response.redirect_permanent(*args, **kwargs)


class RequestParseError(BadRequest):
    """\
    An error was encountered while parsing the HTTP request.
    """


class MethodNotAllowed(ResponseException):
    """\
    The URL is valid, but does not respond to the requested method
    """
    def __init__(self, valid_methods):
        super(MethodNotAllowed, self).__init__(valid_methods)
        self.response = Response.method_not_allowed(valid_methods)
