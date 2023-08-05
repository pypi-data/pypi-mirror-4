"""
Utility functions for HTTP message parsing

Copyright (c) 2009-2012 Oliver Cope. All rights reserved.
See LICENSE.txt for terms of redistribution and use.
"""

import re
from email.message import Message
try:
    from email.parser import BytesParser
except ImportError:
    # python 2
    from email.parser import Parser as BytesParser  # NOQA

try:
    from urllib.parse import unquote_plus
except ImportError:
    from urllib import unquote_plus  # NOQA
from shutil import copyfileobj

import fresco
from fresco.compat import PY3, string_types
from fresco.exceptions import RequestParseError
from fresco.util.io import ExpandableOutput, SizeLimitedInput, PutbackInput, \
                           DelimitedInput

KB = 1024
MB = 1024 * KB

#: Data chunk size to read from the input stream (wsgi.input)
CHUNK_SIZE = 8 * KB


class TooBig(RequestParseError):
    """\
    Request body is too big
    """
    def __init__(self, *args, **kwargs):
        super(TooBig, self).__init__(*args, **kwargs)
        self.response = fresco.response.Response.request_entity_too_large()


class MissingContentLength(RequestParseError):
    """\
    No ``Content-Length`` header given
    """
    def __init__(self, *args, **kwargs):
        super(MissingContentLength, self).__init__(*args, **kwargs)
        self.response = fresco.response.Response.length_required()


def dequote(s):
    """\
    Return ``s`` with surrounding quotes removed. Example usage::

        >>> dequote('foo')
        'foo'
        >>> dequote('"foo"')
        'foo'
    """
    if len(s) > 1 and s[0] == '"' == s[-1]:
        return s[1:-1]
    return s


def parse_header(header):
    """\
    Given a header, return a tuple of
    ``(value, [(parameter_name, parameter_value)])``.

    Example usage::

        >>> parse_header("text/html; charset=UTF-8")
        ('text/html', {'charset': 'UTF-8'})
        >>> parse_header("multipart/form-data; boundary=-------7d91772e200be")
        ('multipart/form-data', {'boundary': '-------7d91772e200be'})
    """
    items = header.split(';')
    pairs = [
        (name, dequote(value))
             for name, value in (
                 item.lstrip().split('=', 1)
                    for item in items[1:]
            )
    ]
    return (items[0], dict(pairs))


def parse_querystring(data, charset=None, strict=False, keep_blank_values=True,
                      pairsplitter=re.compile('[;&]').split):
    """\
    Return ``(key, value)`` pairs from the given querystring::

        >>> list(parse_querystring('green%20eggs=ham;me=sam+i+am'))
        [('green eggs', u'ham'), (u'me', u'sam i am')]

    :param data: The query string to parse.
    :param charset: Character encoding used to decode values. If not specified,
                    ``fresco.DEFAULT_CHARSET`` will be used.

    :param keep_blank_values: if True, keys without associated values will be
                              returned as empty strings. if False, no key,
                              value pair will be returned.

    :param strict: if ``True``, a ``ValueError`` will be raised on parsing
                   errors.
    """

    if charset is None:
        charset = fresco.DEFAULT_CHARSET

    if PY3:
        unquote = lambda s: unquote_plus(s, charset)
    else:
        unquote = lambda s: unquote_plus(s).encode('iso-8859-1')\
                                           .decode(charset)

    for item in pairsplitter(data):
        if not item:
            continue
        try:
            key, value = item.split('=', 1)
        except ValueError:
            if strict:
                raise RequestParseError("bad query field: %r" % (item,))
            if not keep_blank_values:
                continue
            key, value = item, ''

        try:
            yield (unquote(key), unquote(value))
        except UnicodeDecodeError:
            raise RequestParseError("Invalid character data: can't decode"\
                                    " as %r" % (charset,))


def parse_post(environ, fp, default_charset=None, max_size=16 * KB,
               max_multipart_size=2 * MB):
    """\
    Parse the contents of an HTTP POST request, which may be either
    application/x-www-form-urlencoded or multipart/form-data encoded.

    Returned items are either tuples of (name, value) for simple string values
    or (name, FileUpload) for uploaded files.

    :param max_multipart_size: Maximum size of total data for a multipart form
                               submission

    :param max_size: The maximum size of data allowed to be read into memory.
                     For a application/x-www-form-urlencoded submission, this
                     is the maximum size of the entire data. For a
                     multipart/form-data submission, this is the maximum size
                     of any individual field (except file uploads).
    """
    ct, ct_params = parse_header(
        environ.get('CONTENT_TYPE', 'application/x-www-form-urlencoded')
    )

    if default_charset is None:
        default_charset = fresco.DEFAULT_CHARSET
    charset = ct_params.get('charset', default_charset)

    try:
        content_length = int(environ['CONTENT_LENGTH'])
    except (TypeError, ValueError, KeyError):
        raise MissingContentLength()

    if ct == 'application/x-www-form-urlencoded':
        if content_length > max_size:
            raise TooBig("Content Length exceeds permitted size")
        return parse_querystring(SizeLimitedInput(fp, content_length)
                                    .read()
                                    .decode('ASCII'), charset)
    else:
        if content_length > max_multipart_size:
            raise TooBig("Content Length exceeds permitted size")
        try:
            boundary = ct_params['boundary']
        except KeyError:
            raise RequestParseError("No boundary given in multipart/form-data"\
                                    " content-type")
        return parse_multipart(SizeLimitedInput(fp, content_length),
                               boundary.encode('ascii'), charset, max_size)


class HTTPMessage(Message):
    """
    Represent HTTP request message headers
    """


def parse_multipart(fp, boundary, default_charset, max_size):
    """
    Parse data encoded as ``multipart/form-data``. Generate tuples of::

        (<field-name>, <data>)

    Where ``data`` will be a string in the case of a regular input field, or a
    ``FileUpload`` instance if a file was uploaded.

    :param fp: input stream from which to read data
    :param boundary: multipart boundary string, as specified by the
                     ``Content-Disposition`` header
    :param default_charset: character set to use for encoding, if not specified
                            by a content-type header. In practice web browsers
                            don't supply a content-type header so this needs to
                            contain a sensible value.
    :param max_size: Maximum size in bytes for any non file upload part
    """

    boundary_size = len(boundary)
    if not boundary.startswith(b'--'):
        raise RequestParseError("Malformed boundary string:"\
                                " must start with '--' (rfc 2046)")

    if boundary_size > 72:
        raise RequestParseError("Malformed boundary string:"\
                                " must be no more than 70 characters, not"\
                                " counting the two leading hyphens (rfc 2046)")

    assert boundary_size + 2 < CHUNK_SIZE, \
          "CHUNK_SIZE cannot be smaller than the boundary string"

    if fp.read(2) != b'--':
        raise RequestParseError("Malformed POST data: expected two hypens")

    if fp.read(boundary_size) != boundary:
        raise RequestParseError("Malformed POST data: expected boundary")

    if fp.read(2) != b'\r\n':
        raise RequestParseError("Malformed POST data: expected CRLF")

    fp = PutbackInput(fp)

    while True:
        headers, data = _read_multipart_field(fp, boundary)
        try:
            _, params = parse_header(headers['Content-Disposition'])
        except KeyError:
            raise RequestParseError("Missing Content-Disposition header")

        try:
            name = params['name']
        except KeyError:
            raise RequestParseError("Missing name parameter in"\
                                    " Content-Disposition header")

        is_file_upload = 'Content-Type' in headers and 'filename' in params

        if is_file_upload:
            storage = data.getstorage()
            storage.seek(0)
            yield name, FileUpload(params['filename'], headers, storage)

        else:
            charset = parse_header(headers.get('Content-Type', ''))[1]\
                      .get('charset', default_charset)
            if data.tell() > max_size:
                raise TooBig("Data block exceeds maximum permitted size")
            try:
                data.seek(0)
                yield name, data.read().decode(charset)
            except UnicodeDecodeError:
                raise RequestParseError("Invalid character data: can't decode"\
                                        " as %r" % (charset,))

        chunk = fp.read(2)
        if chunk == b'--':
            if fp.peek(3) != b'\r\n':
                raise RequestParseError("Expected terminating CRLF"\
                                        " at end of stream")
            break

        if chunk != b'\r\n':
            raise RequestParseError("Expected CRLF after boundary")


def _read_multipart_field(fp, boundary):
    """
    Read a single part from a multipart/form-data message and return a tuple of
    ``(headers, data)``. Stream ``fp`` must be positioned at the start of the
    header block for the field.

    Return a tuple of ('<headers>', '<data>')

    ``headers`` is an instance of ``email.message.Message``.

    ``data`` is an instance of ``ExpandableOutput``.

    Note that this currently cannot handle nested multipart sections.
    """
    data = ExpandableOutput()
    headers = BytesParser(_class=HTTPMessage).parse(
        DelimitedInput(fp, b'\r\n\r\n'),
        headersonly=True
    )
    fp = DelimitedInput(fp, b'\r\n--' + boundary)

    # XXX: handle base64 encoding etc
    for chunk in iter(lambda: fp.read(CHUNK_SIZE), b''):
        data.write(chunk)
    data.flush()

    # Fallen off the end of the input without having read a complete field?
    if not fp.delimiter_found:
        raise RequestParseError("Incomplete data (expected boundary)")

    return headers, data


class FileUpload(object):
    """\
    Represent a file uploaded in an HTTP form submission
    """

    def __init__(self, filename, headers, fileob):

        self.filename = filename
        self.headers = headers
        self.file = fileob

        # UNC/Windows path
        if self.filename[:2] == '\\\\' or self.filename[1:3] == ':\\':
            self.filename = self.filename[self.filename.rfind('\\') + 1:]

    def save(self, fileob):
        """
        Save the upload to the file object or path ``fileob``

        :param fileob: a file-like object open for writing, or the path to the
                       file to be written
        """
        if isinstance(fileob, string_types):
            with open(fileob, 'wb') as f:
                return self.save(f)

        self.file.seek(0)
        copyfileobj(self.file, fileob)
