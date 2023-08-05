# flake8: noqa

from sys import version_info

PY3 = version_info > (3, 0)
PY33 = version_info >= (3, 3)

if PY3:
    string_types = (str,)
    ustring_type = str
else:
    string_types = (basestring,)
    ustring_type = unicode

if PY33:
    from threading import get_ident

elif PY3:
    from _thread import get_ident

else:
    from thread import get_ident

if PY3:
    from urllib.parse import quote, quote_plus, unquote, urlparse, urlunparse, ParseResult

else:
    from urllib import quote, quote_plus, unquote
    from urlparse import urlparse, urlunparse, ParseResult

__all__ = 'PY3', 'string_types', 'ustring_type',\
          'get_ident', 'quote', 'quote_plus', 'unquote', 'urlparse', \
          'ParseResult'

