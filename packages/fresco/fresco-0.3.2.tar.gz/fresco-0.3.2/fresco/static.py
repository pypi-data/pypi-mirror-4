"""
Utilities for dealing with static file content
"""

import mimetypes
import os
from email.utils import formatdate, parsedate_tz, mktime_tz

from fresco import context
from fresco.exceptions import NotFound, Forbidden
from fresco.response import Response, STATUS_OK, STATUS_NOT_MODIFIED
from fresco.util.wsgi import ClosingIterator

__all__ = 'serve_static_file',


def serve_static_file(path, default_charset="ISO-8859-1",
                      bufsize=8192):
    """
    Serve a static file located at ``path``.

    :returns: A :class:`~fresco.response.Response` object for the file at
              ``path``
    """

    try:
        mtime = os.path.getmtime(path)
    except OSError:
        raise NotFound()

    request = context.request
    mod_since = request.get_header('if-modified-since')
    if mod_since is not None:
        mod_since = mktime_tz(parsedate_tz(mod_since))
        if int(mtime) <= int(mod_since):
            return Response(status=STATUS_NOT_MODIFIED)

    typ, enc = mimetypes.guess_type(path)
    if typ is None:
        typ = 'application/octet-stream'
    if typ.startswith('text/'):
        typ = typ + '; charset=%s' % default_charset

    if 'wsgi.file_wrapper' in request.environ:
        content_iterator = lambda f: \
                request.environ['wsgi.file_wrapper'](f, bufsize)
    else:
        content_iterator = lambda f: \
                ClosingIterator(iter(lambda: f.read(bufsize), ''), f.close)

    try:
        _file = open(path, 'rb')
    except IOError:
        raise Forbidden()

    return Response(
        status=STATUS_OK,
        content_length=str(os.path.getsize(path)),
        last_modified=formatdate(mtime, localtime=False, usegmt=True),
        content_type=typ,
        content_encoding=enc,
        content=content_iterator(_file)
    )
