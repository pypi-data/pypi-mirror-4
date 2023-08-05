"""
The :class:`Response` class models the response from your application to a
single request.
"""

import re
from itertools import chain

import fresco
from .cookie import Cookie

__all__ = [
    'STATUS_CONTINUE', 'STATUS_SWITCHING_PROTOCOLS',
    'STATUS_OK', 'STATUS_CREATED', 'STATUS_ACCEPTED',
    'STATUS_NON_AUTHORITATIVE_INFORMATION', 'STATUS_NO_CONTENT',
    'STATUS_RESET_CONTENT', 'STATUS_PARTIAL_CONTENT',
    'STATUS_MULTIPLE_CHOICES', 'STATUS_MOVED_PERMANENTLY', 'STATUS_FOUND',
    'STATUS_SEE_OTHER', 'STATUS_NOT_MODIFIED', 'STATUS_USE_PROXY',
    'STATUS_TEMPORARY_REDIRECT', 'STATUS_BAD_REQUEST', 'STATUS_UNAUTHORIZED',
    'STATUS_PAYMENT_REQUIRED', 'STATUS_FORBIDDEN', 'STATUS_NOT_FOUND',
    'STATUS_METHOD_NOT_ALLOWED', 'STATUS_NOT_ACCEPTABLE',
    'STATUS_PROXY_AUTHENTICATION_REQUIRED', 'STATUS_REQUEST_TIME_OUT',
    'STATUS_CONFLICT', 'STATUS_GONE', 'STATUS_LENGTH_REQUIRED',
    'STATUS_PRECONDITION_FAILED', 'STATUS_REQUEST_ENTITY_TOO_LARGE',
    'STATUS_REQUEST_URI_TOO_LARGE', 'STATUS_UNSUPPORTED_MEDIA_TYPE',
    'STATUS_REQUESTED_RANGE_NOT_SATISFIABLE', 'STATUS_EXPECTATION_FAILED',
    'STATUS_INTERNAL_SERVER_ERROR', 'STATUS_NOT_IMPLEMENTED',
    'STATUS_BAD_GATEWAY', 'STATUS_SERVICE_UNAVAILABLE',
    'STATUS_GATEWAY_TIME_OUT', 'STATUS_HTTP_VERSION_NOT_SUPPORTED',
    'Response'
]


#: HTTP/1.1 status codes as listed in http://www.ietf.org/rfc/rfc2616.txt
HTTP_STATUS_CODES = {
      100: 'Continue',
      101: 'Switching Protocols',
      200: 'OK',
      201: 'Created',
      202: 'Accepted',
      203: 'Non-Authoritative Information',
      204: 'No Content',
      205: 'Reset Content',
      206: 'Partial Content',
      300: 'Multiple Choices',
      301: 'Moved Permanently',
      302: 'Found',
      303: 'See Other',
      304: 'Not Modified',
      305: 'Use Proxy',
      307: 'Temporary Redirect',
      400: 'Bad Request',
      401: 'Unauthorized',
      402: 'Payment Required',
      403: 'Forbidden',
      404: 'Not Found',
      405: 'Method Not Allowed',
      406: 'Not Acceptable',
      407: 'Proxy Authentication Required',
      408: 'Request Time-out',
      409: 'Conflict',
      410: 'Gone',
      411: 'Length Required',
      412: 'Precondition Failed',
      413: 'Request Entity Too Large',
      414: 'Request-URI Too Large',
      415: 'Unsupported Media Type',
      416: 'Requested range not satisfiable',
      417: 'Expectation Failed',
      500: 'Internal Server Error',
      501: 'Not Implemented',
      502: 'Bad Gateway',
      503: 'Service Unavailable',
      504: 'Gateway Time-out',
      505: 'HTTP Version not supported',
}

# Symbolic names for the HTTP status codes
STATUS_CONTINUE = 100
STATUS_SWITCHING_PROTOCOLS = 101
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_ACCEPTED = 202
STATUS_NON_AUTHORITATIVE_INFORMATION = 203
STATUS_NO_CONTENT = 204
STATUS_RESET_CONTENT = 205
STATUS_PARTIAL_CONTENT = 206
STATUS_MULTIPLE_CHOICES = 300
STATUS_MOVED_PERMANENTLY = 301
STATUS_FOUND = 302
STATUS_SEE_OTHER = 303
STATUS_NOT_MODIFIED = 304
STATUS_USE_PROXY = 305
STATUS_TEMPORARY_REDIRECT = 307
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_PAYMENT_REQUIRED = 402
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_METHOD_NOT_ALLOWED = 405
STATUS_NOT_ACCEPTABLE = 406
STATUS_PROXY_AUTHENTICATION_REQUIRED = 407
STATUS_REQUEST_TIME_OUT = 408
STATUS_CONFLICT = 409
STATUS_GONE = 410
STATUS_LENGTH_REQUIRED = 411
STATUS_PRECONDITION_FAILED = 412
STATUS_REQUEST_ENTITY_TOO_LARGE = 413
STATUS_REQUEST_URI_TOO_LARGE = 414
STATUS_UNSUPPORTED_MEDIA_TYPE = 415
STATUS_REQUESTED_RANGE_NOT_SATISFIABLE = 416
STATUS_EXPECTATION_FAILED = 417
STATUS_INTERNAL_SERVER_ERROR = 500
STATUS_NOT_IMPLEMENTED = 501
STATUS_BAD_GATEWAY = 502
STATUS_SERVICE_UNAVAILABLE = 503
STATUS_GATEWAY_TIME_OUT = 504
STATUS_HTTP_VERSION_NOT_SUPPORTED = 505


#: Mapping from python symbolic names to HTTP headers to ensure headers are
#: emitted with correct capitalization
HEADER_NAMES = {
    'accept_ranges': 'Accept-Ranges',
    'age': 'Age',
    'allow': 'Allow',
    'cache_control': 'Cache-Control',
    'connection': 'Connection',
    'content_encoding': 'Content-Encoding',
    'content_language': 'Content-Language',
    'content_length': 'Content-Length',
    'content_location': 'Content-Location',
    'content_md5': 'Content-MD5',
    'content_disposition': 'Content-Disposition',
    'content_range': 'Content-Range',
    'content_type': 'Content-Type',
    'date': 'Date',
    'etag': 'ETag',
    'expires': 'Expires',
    'last_modified': 'Last-Modified',
    'link': 'Link',
    'location': 'Location',
    'p3p': 'P3P',
    'pragma': 'Pragma',
    'proxy_authenticate': 'Proxy-Authenticate',
    'refresh': 'Refresh',
    'retry_after': 'Retry-After',
    'server': 'Server',
    'set_cookie': 'Set-Cookie',
    'strict_transport_security': 'Strict-Transport-Security',
    'trailer': 'Trailer',
    'transfer_encoding': 'Transfer-Encoding',
    'vary': 'Vary',
    'via': 'Via',
    'warning': 'Warning',
    'www_authenticate': 'WWW-Authenticate',
    'x_frame_options': 'X-Frame-Options',
    'x_content_type_options': 'X-Content-Type-Options',
    'x_forwarded_proto': 'X-Forwarded-Proto',
    'front_end_https': 'Front-End-Https',
    'x_powered_by': 'X-Powered-By',
    'x_ua_compatible': 'X-UA-Compatible',
}


def encoder(stream, charset):
    r"""\
    Encode a response iterator using the given character set.

    Synopsis::

        >>> list(encoder(['Price \u00a3200'], 'latin1'))
        [b'Price \xa3200']
    """
    if charset is None:
        charset = 'UTF-8'

    for chunk in stream:
        if not isinstance(chunk, bytes):
            yield chunk.encode(charset)
        else:
            yield chunk


class Response(object):
    """\
    Model an HTTP response
    """

    default_content_type = "text/html; charset=UTF-8"

    def __init__(self, content=None, status="200 OK", headers=None,
                 onclose=None, _nocontent=[], **kwargs):
        """
        Create a new Response object, modelling the HTTP status, headers and
        content of an HTTP response. Response instances are valid WSGI
        applications.

        :param content: The response content as an iterable object
        :param status: The HTTP status line, eg ``200 OK`` or ``404 Not Found``
        :param headers: A list of HTTP headers
        :param kwargs: Arbitrary headers, provided as keyword arguments.
                       Underscores will be replaced with hyphens (eg
                       ``content_length`` becomes ``Content-Length``).

        Example usage::

            >>> # Construct a response
            >>> r = Response(
            ...     content=['hello world'],
            ...     status='200 OK',
            ...     headers=[('Content-Type', 'text/plain')]
            ... )
            >>>

        Changing headers or content::

            >>> r = r.add_header('X-Header', 'hello!')
            >>> r = r.replace(content=['whoa nelly!'],
            ...               content_type='text/html')

        """

        if content is None:
            content = _nocontent

        self._content = content
        self._status = make_status(status)
        if onclose is None:
            self.onclose = []
        elif callable(onclose):
            self.onclose = [onclose]
        else:
            self.onclose = list(onclose)

        if headers is None:
            headers = []
        headers = make_headers(headers, kwargs)

        # Ensure a content-type header is set if a content iterator has been
        # provided
        if content is not _nocontent:
            for key, value in headers:
                if key == 'Content-Type':
                    break
            else:
                headers.insert(0, ('Content-Type', self.default_content_type))

        self._headers = headers

    def __call__(self, environ, start_response, exc_info=None):
        """
        WSGI callable. Calls ``start_response`` with assigned headers and
        returns an iterator over ``content``.
        """
        start_response(
            self.status,
            self.headers,
            exc_info,
        )
        result = _copy_close(self.content, encoder(self.content, self.charset))
        if self.onclose:
            result = ClosingIterator(result, *self.onclose)
        return result

    def add_onclose(self, *funcs):
        """
        Add functions to be called as part of the response iterators ``close``
        method.
        """
        return self.__class__(
            self.content,
            self.status,
            self.headers,
            self.onclose + list(funcs),
            add_default_content_type=False
        )

    @classmethod
    def from_wsgi(cls, wsgi_callable, environ, start_response):
        """
        Return a ``Response`` object constructed from the result of calling
        ``wsgi_callable`` with the given ``environ`` and ``start_response``
        arguments.
        """
        responder = StartResponseWrapper(start_response)
        content = wsgi_callable(environ, responder)
        if responder.buf.tell():
            content = _copy_close(content,
                                  chain(content, [responder.buf.getvalue()]))

        if responder.called:
            return cls(content, responder.status, headers=responder.headers)

        # Iterator has not called start_response yet. Call content.next()
        # to force the application to call start_response
        try:
            chunk = content.next()
        except StopIteration:
            return cls(content, responder.status, headers=responder.headers)
        except Exception:
            close = getattr(content, 'close', None)
            if close is not None:
                close()
            raise
        content = _copy_close(content, chain([chunk], content))
        return cls(
            content,
            responder.status,
            headers=responder.headers
        )

    @property
    def content(self):
        """
        Iterator over the response content part
        """
        return self._content

    @property
    def headers(self):
        """\
        Return a list of response headers in the format
        ``[(<header-name>, <value>), ...]``
        """
        return self._headers

    def get_headers(self, name):
        """\
        Return the list of headers set with the given name.

        Synopsis::

            >>> r = Response(set_cookie = ['cookie1', 'cookie2'])
            >>> r.get_headers('set-cookie')
            ['cookie1', 'cookie2']

        """
        return [value for header, value in self.headers
                      if header.lower() == name.lower()]

    def get_header(self, name, default=''):
        """\
        Return the concatenated values of the named header(s) or ``default`` if
        the header has not been set.

        As specified in RFC2616 (section 4.2), multiple headers will be
        combined using a single comma.

        Example usage::

            >>> r = Response(set_cookie = ['cookie1', 'cookie2'])
            >>> r.get_header('set-cookie')
            'cookie1,cookie2'
        """
        headers = self.get_headers(name)
        if not headers:
            return default
        return ','.join(headers)

    @property
    def status(self):
        """\
        HTTP status message for the response, eg ``200 OK``
        """
        return self._status

    @property
    def status_code(self):
        """\
        Return the numeric status code for the response as an integer::

            >>> Response(status='404 Not Found').status_code
            404
            >>> Response(status=200).status_code
            200
        """
        return int(self._status.split(' ', 1)[0])

    @property
    def content_type(self):
        """\
        Return the value of the ``Content-Type`` header if set, otherwise
        ``None``.
        """
        for key, val in self.headers:
            if key.lower() == 'content-type':
                return val
        return None

    def add_header(self, name, value):
        """\
        Return a new response object with the given additional header.

        Synopsis::

            >>> r = Response(content_type='text/plain')
            >>> r.headers
            [('Content-Type', 'text/plain')]
            >>> r.add_header('Cache-Control', 'no-cache').headers
            [('Content-Type', 'text/plain'), ('Cache-Control', 'no-cache')]
        """
        return self.replace(self._content, self._status,
                            self._headers + [(name, value)])

    def add_headers(self, headers=[], **kwheaders):
        """\
        Return a new response object with the given additional headers.

        Synopsis::

            >>> r = Response(content_type='text/plain')
            >>> r.headers
            [('Content-Type', 'text/plain')]
            >>> r.add_headers(
            ...     cache_control='no-cache',
            ... ).headers
            [('Content-Type', 'text/plain'), ('Cache-Control', 'no-cache')]
        """
        return self.replace(headers=make_headers(self._headers + headers,
                                                      kwheaders))

    def remove_headers(self, *headers):
        """\
        Return a new response object with the given headers removed.

        Synopsis::

            >>> r = Response(content_type='text/plain',
            ...              cache_control='no-cache')
            >>> r.headers
            [('Cache-Control', 'no-cache'), ('Content-Type', 'text/plain')]
            >>> r.remove_headers('Cache-Control').headers
            [('Content-Type', 'text/plain')]
        """
        toremove = [item.lower() for item in headers]
        return self.replace(headers=[h for h in self._headers
                                       if h[0].lower() not in toremove])

    def add_cookie(
        self, name, value, maxage=None, expires=None, path=None,
        secure=None, domain=None, comment=None, http_only=False, version=1
    ):
        """\
        Return a new response object with the given cookie added.

        Synopsis::

            >>> r = Response(content_type='text/plain')
            >>> r.headers
            [('Content-Type', 'text/plain')]
            >>> r.add_cookie('a', '1').headers
            [('Content-Type', 'text/plain'), ('Set-Cookie', 'a=1;Version=1')]
        """
        return self.replace(
            headers=self._headers + [
                (
                    'Set-Cookie',
                    Cookie(
                        name, value, maxage, expires, path,
                        secure, domain,
                        comment=comment,
                        http_only=http_only,
                        version=version
                    )
                )
            ]
        )

    def replace(self, content=None, status=None, headers=None, **kwheaders):
        """\
        Return a new response object with any of content, status or headers
        changed.

        Synopsis::

            >>> r = Response(content_type='text/html')
            >>> r = r.replace(content='foo',
            ...               status=404,
            ...               headers=[('Content-Type', 'text/plain')],
            ...               content_length=3)

        """

        res = self

        if content is not None:
            close = getattr(self.content, 'close', None)
            onclose = self.onclose
            if close:
                onclose = [close] + onclose
            res = res.__class__(content, res._status, res._headers,
                                onclose=onclose, content_type=None)

        if headers is not None:
            res = res.__class__(res._content, res._status, headers,
                                onclose=res.onclose, content_type=None)

        if status is not None:
            res = res.__class__(res._content, status, res._headers,
                                onclose=res.onclose, content_type=None)

        if kwheaders:
            toremove = set(make_header_name(k) for k in kwheaders)
            kwheaders = make_headers([], kwheaders)
            res = res.__class__(
                res._content,
                res._status,
                [(key, value) for key, value in res._headers
                              if key not in toremove] + kwheaders,
                onclose=res.onclose,
                add_default_content_type=False
            )

        return res

    def buffered(self):
        """\
        Return a new response object with the content buffered into a list.
        This will also generate a content-length header.

        Example usage::

            >>> def generate_content():
            ...     yield "one two "
            ...     yield "three four five"
            ...
            >>> r = Response(content=generate_content())
            >>> r.content  # doctest: +ELLIPSIS
            <generator object ...>
            >>> r = Response(content=generate_content()).buffered()
            >>> r.content
            ['one two ', 'three four five']
        """
        content = list(self.content)
        content_length = sum(map(len, content))
        return self.replace(content=content, content_length=content_length)

    @property
    def charset(
        self,
        _parser=re.compile(r'.*;\s*charset=([\w\d\-]+)', re.I).match
    ):
        for key, val in self.headers:
            if key.lower() == 'content-type':
                mo = _parser(val)
                if mo:
                    return mo.group(1)
                else:
                    return None
        return None

    @classmethod
    def not_found(cls, request=None):
        """\
        Return an HTTP not found response (404).

        Synopsis::

            >>> def view():
            ...     return Response.not_found()
            ...
        """
        return cls(
            status=STATUS_NOT_FOUND,
            content=[
                "<html>\n"
                "<body>\n"
                "    <h1>Not found</h1>\n"
                "    <p>The requested resource could not be found.</p>\n"
                "</body>\n"
                "</html>"
            ]
        )

    @classmethod
    def forbidden(cls, message='Sorry, access is denied'):
        """\
        Return an HTTP forbidden response (403).

        Synopsis::

            >>> def view():
            ...     return Response.forbidden()
            ...
        """
        return cls(
            status=STATUS_FORBIDDEN,
            content=[
                "<html>\n"
                "<body>\n"
                "<h1>" + message + "</h1>\n"
                "</body>\n"
                "</html>"
            ]
        )

    @classmethod
    def bad_request(cls, request=None):
        """\
        Return an HTTP bad request response.

        Synopsis::

            >>> def view():
            ...     return Response.bad_request()
            ...

        """
        return cls(
            status=STATUS_BAD_REQUEST,
            content=[
                "<html>"
                "<body>"
                "<h1>The server could not understand your request</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def length_required(cls, request=None):
        """\
        Return an HTTP Length Required response (411).

        Synopsis::

            >>> def view():
            ...     return Response.length_required()
            ...

        """
        return cls(
            status=STATUS_LENGTH_REQUIRED,
            content=[
                "<html>"
                "<body>"
                "<h1>A Content-Length header is required</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def request_entity_too_large(cls, request=None):
        """\
        Return an HTTP Request Entity Too Large response (413).

        Example usage::

            >>> from flea import TestAgent
            >>> response = Response.request_entity_too_large()
            >>> print TestAgent(response).get('/', check_status=False)
            413 Request Entity Too Large\r
            Content-Type: text/html; charset=UTF-8\r
            \r
            <html><body><h1>Request Entity Too Large</h1></body></html>

        """
        return cls(
            status=STATUS_REQUEST_ENTITY_TOO_LARGE,
            content=["<html>"
                "<body>"
                    "<h1>Request Entity Too Large</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def method_not_allowed(cls, valid_methods):
        """\
        Return an HTTP method not allowed response (405)::

            >>> def view():
            ...     if request.method == 'POST':
            ...         return Response.method_not_allowed(('POST', ))
            ...

        :param valid_methods: A list of HTTP methods valid for requested URL

        :return: A :class:`fresco.response.Response` instance
        """

        return cls(
            status=STATUS_METHOD_NOT_ALLOWED,
            allow=",".join(valid_methods),
            content=["<html>"
                "<body>"
                    "<h1>Method not allowed</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def internal_server_error(cls):
        """\
        Return an HTTP internal server error response (500).

        Synopsis::

            >>> def view():
            ...     return Response.internal_server_error()
            ...

        :return: A :class:`fresco.response.Response` instance
        """

        return cls(
            status=STATUS_INTERNAL_SERVER_ERROR,
            content=[
                "<html>"
                "<body>"
                "<h1>Internal Server Error</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def redirect(cls, location, request=None, status=STATUS_FOUND):
        """\
        Return an HTTP redirect reponse (302 or 301).

        :param location: The redirect location.
        :param status: HTTP status code for the redirect, default is
                       ``STATUS_FOUND`` (temporary redirect)

        Synopsis:

            >>> def view():
            ...   return Response.redirect("/new-location")
            ...
        """
        if '://' not in location:
            if request is None:
                request = fresco.context.request
            location = request.resolve_url(location)
        return Response(
            status=status,
            location=location,
            content=[
                "<html><head></head><body>\n",
                "<h1>Page has moved</h1>\n",
                "<p><a href='%s'>%s</a></p>\n" % (location, location),
                "</body></html>",
            ]
        )

    @classmethod
    def redirect_permanent(cls, *args, **kwargs):
        """\
        Return an HTTP permanent redirect reponse.

        :param location: the URI of the new location. If relative this will be
                         converted to an absolute URL based on the current
                         request.

        """
        return cls.redirect(status=STATUS_MOVED_PERMANENTLY, *args, **kwargs)

    @classmethod
    def redirect_temporary(cls, *args, **kwargs):
        """\
        Return an HTTP permanent redirect reponse.

        :param location: the URI of the new location. If relative this will be
                         converted to an absolute URL based on the current
                         request.

        """
        return cls.redirect(status=STATUS_FOUND, *args, **kwargs)

    @classmethod
    def meta_refresh(cls, location, delay=1, request=None):
        """\
        Return an HTML page containing a <meta http-equiv="refresh"> tag,
        causing the browser to redirect to the given location after ``delay``
        seconds.

        :param location: the URI of the new location. If relative this will be
                         converted to an absolute URL based on the current
                         request.

        """
        if '://' not in location:
            if request is None:
                request = fresco.context.request
            location = request.resolve_url(location)
        return cls([(
            '<!DOCTYPE html>'
            '<html>'
            '<head><meta http-equiv="refresh" content="0; url={0}"></head>'
            '<body><p><a href="{0}">Click here to continue</a></p></body>'
            '</html>').format(location)
        ], content_type='text/html')


def make_header_name(name):
    """\
    Return a formatted header name from a python idenfier.

    Example usage::

        >>> make_header_name('content_type')
        'Content-Type'
    """
    try:
        return HEADER_NAMES[name]
    except KeyError:
        return name.replace('_', '-').title()


def make_headers(header_list, header_dict):
    """
    Return a list of header (name, value) tuples from the combination of
    the header_list and header_dict.

    Synopsis::

        >>> make_headers(
        ...     [('Content-Type', 'text/html')],
        ...     {'content_length' : 54}
        ... )
        [('Content-Type', 'text/html'), ('Content-Length', '54')]

        >>> make_headers(
        ...     [('Content-Type', 'text/html')],
        ...     {'x_foo' : ['a1', 'b2']}
        ... )
        [('Content-Type', 'text/html'), ('X-Foo', 'a1'), ('X-Foo', 'b2')]

    """
    headers = header_list + list(header_dict.items())
    headers = [(make_header_name(key), val)
               for key, val in headers if val is not None]

    # Join multiple headers, see RFC2616 section 4.2
    newheaders = []
    for key, val in headers:
        if isinstance(val, list):
            for item in val:
                newheaders.append((key, str(item)))
        else:
            newheaders.append((key, str(val)))
    return newheaders


def dump_response(r, line_break='\r\n'):
    """\
    Return a string representation of the given response, as for a HTTP
    response.
    """
    output = []
    output.append(r.status)
    output.append(line_break)
    output.extend('{}: {}{}'.format(k, v, line_break)
                  for k, v in sorted(r.headers))
    output.append(line_break)
    output.extend(r.content)
    return ''.join(output)


def make_status(status):
    """
    Return a status line from the given status, which may be a simple integer.

    Synopsis::

        >>> make_status(200)
        '200 OK'

    """
    if isinstance(status, int):
        return '%d %s' % (status, HTTP_STATUS_CODES[status])
    return status


def _copy_close(src, dst, marker=object()):
    """\
    Copy the ``close`` attribute from ``src`` to ``dst``, which are assumed to
    be iterators.

    If it is not possible to copy the attribute over (eg for
    ``itertools.chain``, which does not support the close attribute) an
    instance of ``ClosingIterator`` is returned which will proxy calls to
    ``close`` as necessary.
    """

    close = getattr(src, 'close', marker)
    if close is not marker:
        try:
            setattr(dst, 'close', close)
        except AttributeError:
            return ClosingIterator(dst, close)

    return dst

from .util.wsgi import StartResponseWrapper, ClosingIterator
