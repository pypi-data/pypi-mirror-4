"""\
Utilities for interfacing with WSGI
"""

from functools import partial
from io import BytesIO

from fresco.compat import PY3

__all__ = 'environ_to_unicode', 'unicode_to_environ',\
          'environ_to_bytes', 'bytes_to_environ',\
          'StartResponseWrapper', 'ClosingIterator'


def with_docstring_from(src):
    def with_docstring_from(tgt):
        try:
            tgt.__doc__ = src.__doc__
        except AttributeError:
            tgt.func_doc = src.func_doc
        return tgt
    return with_docstring_from


def _environ_to_unicode_py2(s, enc='UTF-8'):
    """
    Decode a WSGI environ value to a unicode string
    """
    return s.decode(enc)


@with_docstring_from(_environ_to_unicode_py2)
def _environ_to_unicode_py3(s, enc='UTF-8'):
    return s.encode('iso-8859-1').decode(enc)


def _unicode_to_environ_py2(s, enc='UTF-8'):
    """
    Return a unicode string encoded for a WSGI environ value

    For python 2, this simply returns ``s`` encoded using the specified
    encoding

    For python 3 this returns a 'bytes-as-unicode' string:

    - encode ``s`` using the specified encoding (eg utf8)
    - decode the resulting byte string as latin-1
    """
    return s.encode(enc, 'surrogateescape')


@with_docstring_from(_unicode_to_environ_py2)
def _unicode_to_environ_py3(s, enc='UTF-8'):
    return s.encode(enc, 'surrogateescape').decode('iso-8859-1')


def _environ_to_bytes_py2(s):
    """
    Decode a WSGI environ value to a bytes object
    """
    return s


@with_docstring_from(_environ_to_bytes_py2)
def _environ_to_bytes_py3(s):
    return s.encode('latin1')


def _bytes_to_environ_py2(s):
    """
    Encode a byte string to a WSGI environ value

    For Python 2, this simply returns ``s``.
    For Python 3 this returns a 'bytes-as-unicode' string.
    """
    return s


@with_docstring_from(_environ_to_bytes_py2)
def _bytes_to_environ_py3(s):
    return s.decode('latin1')


if str is bytes:
    environ_to_unicode = _environ_to_unicode_py2
    unicode_to_environ = _unicode_to_environ_py2
    environ_to_bytes = _environ_to_bytes_py2
    bytes_to_environ = _bytes_to_environ_py2

else:
    environ_to_unicode = _environ_to_unicode_py3
    unicode_to_environ = _unicode_to_environ_py3
    environ_to_bytes = _environ_to_bytes_py3
    bytes_to_environ = _bytes_to_environ_py3


class StartResponseWrapper(object):
    """\
    Wrapper class for the ``start_response`` callable, allowing middleware
    applications to intercept and interrogate the proxied start_response
    arguments.

    Synopsis::

        >>> def my_wsgi_app(environ, start_response):
        ...     start_response('200 OK', [('Content-Type', 'text/plain')])
        ...     return ['Whoa nelly!']
        ...
        >>> def my_other_wsgi_app(environ, start_response):
        ...     responder = StartResponseWrapper(start_response)
        ...     result = my_wsgi_app(environ, responder)
        ...     print "Got status", responder.status
        ...     print "Got headers", responder.headers
        ...     responder.call_start_response()
        ...     return result
        ...
        >>> from flea import TestAgent
        >>> result = TestAgent(my_other_wsgi_app).get('/')
        Got status 200 OK
        Got headers [('Content-Type', 'text/plain')]

    See also ``Response.from_wsgi``, which takes a wsgi callable, environ and
    start_response, and returns a ``Response`` object, allowing the client to
    further interrogate and customize the WSGI response.

    Note that it is usually not advised to use this directly in middleware as
    start_response may not be called directly from the WSGI application, but
    rather from the iterator it returns. In this case the middleware may need
    logic to accommodate this. It is usually safer to use
    ``Response.from_wsgi``, which takes this into account.
    """

    def __init__(self, start_response):
        self.start_response = start_response
        self.status = None
        self.headers = []
        self.called = False
        self.buf = BytesIO()
        self.exc_info = None

    def __call__(self, status, headers, exc_info=None):
        """
        Dummy WSGI ``start_response`` function that stores the arguments for
        later use.
        """
        self.status = status
        self.headers = headers
        self.exc_info = exc_info
        self.called = True
        return self.buf.write

    def call_start_response(self):
        """
        Invoke the wrapped WSGI ``start_response`` function.
        """
        try:
            write = self.start_response(
                self.status,
                self.headers,
                self.exc_info
            )
            write(self.buf.getvalue())
            return write
        finally:
            # Avoid dangling circular ref
            self.exc_info = None


class ClosingIterator(object):
    """\
    Wrap a WSGI iterator to allow additional close functions to be called on
    application exit.

    Synopsis::

        >>> class filelikeobject(object):
        ...
        ...     def read(self):
        ...         print "file read!"
        ...         return ''
        ...
        ...     def close(self):
        ...         print "file closed!"
        ...
        >>> def app(environ, start_response):
        ...     f = filelikeobject()
        ...     start_response('200 OK', [('Content-Type', 'text/plain')])
        ...     return ClosingIterator(iter(f.read, ''), f.close)
        ...
        >>> from flea import TestAgent
        >>> m = TestAgent(app).get('/')
        file read!
        file closed!

    """

    def __init__(self, iterable, *close_funcs):
        """
        Initialize a ``ClosingIterator`` to wrap iterable ``iterable``, and
        call any functions listed in ``*close_funcs`` on the instance's
        ``.close`` method.
        """
        self.__dict__['_iterable'] = iterable
        if PY3:
            self.__dict__['_next'] = partial(next, iter(self._iterable))
        else:
            self.__dict__['_next'] = iter(self._iterable).next
        self.__dict__['_close_funcs'] = close_funcs
        iterable_close = getattr(self._iterable, 'close', None)
        if iterable_close is not None:
            self.__dict__['_close_funcs'] = (iterable_close,) + close_funcs
        self.__dict__['_closed'] = False

    def __iter__(self):
        """
        ``__iter__`` method
        """
        return self

    def __next__(self):
        """\
        Return the next item from the iterator
        """
        return self._next()

    def next(self):
        """
        Return the next item from ``iterator``
        """
        return self._next()

    def close(self):
        """
        Call all close functions listed in ``*close_funcs``.
        """
        self.__dict__['_closed'] = True
        for func in self._close_funcs:
            func()

    def __getattr__(self, attr):
        return getattr(self._iterable, attr)

    def __setattr__(self, attr, value):
        return getattr(self._iterable, attr, value)

    def __del__(self):
        """
        Emit a warning if the iterator is deleted with ``close`` having been
        called.
        """
        if not self._closed:
            import warnings
            warnings.warn("%r deleted without close being called" % (self,))
