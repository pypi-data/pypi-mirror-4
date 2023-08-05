# coding=UTF-8
# Copyright (c) 2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

from __future__ import unicode_literals
from io import BytesIO

from nose.tools import assert_equal
from flea import TestAgent

from fresco.compat import quote
from fresco.util.http import parse_querystring, parse_post
from fresco.util.wsgi import unicode_to_environ
from fresco import FrescoApp, context, Response, POST

from . import form_data


class TestParseQueryString(object):

    def p(self, value):
        return list(parse_querystring(value))

    def test_empty(self):
        assert_equal(self.p(''), [])

    def test_simple_key_value(self):
        assert_equal(self.p('a=b'), [('a', 'b')])

    def test_key_with_space(self):
        assert_equal(self.p('a+b=c'), [('a b', 'c')])

    def test_value_with_space(self):
        assert_equal(self.p('a=b+c'), [('a', 'b c')])

    def test_double_equals(self):
        assert_equal(self.p('a==b'), [('a', '=b')])

    def test_escaped_chars(self):
        assert_equal(self.p('%20==c%3D'), [(' ', '=c=')])

    def test_charset(self):
        assert_equal(self.p('a=el%20ni%C3%B1o'), [('a', 'el niño')])


class TestParseMultipart(object):

    def test_multipart(self):
        for data in form_data.multipart_samples:
            io = BytesIO(data['data'])
            io.seek(0)
            environ = {
                'CONTENT_LENGTH': data['content_length'],
                'CONTENT_TYPE': data['content_type'],
            }
            parsed = sorted(list(parse_post(environ, io, 'UTF-8')))

            assert_equal(
                [name for name, value in parsed],
                ["empty-text-input", "file-upload", "text-input-ascii",
                "text-input-unicode"]
            )

            assert_equal(parsed[0], ("empty-text-input", ""))
            assert_equal(parsed[2], ("text-input-ascii", "abcdef"))
            assert_equal(parsed[3], ("text-input-unicode",
                                    b"\xce\xb1\xce\xb2\xce\xb3\xce\xb4"\
                                    .decode("utf8")))

            fieldname, fileupload = parsed[1]
            assert_equal(fieldname, "file-upload")
            assert_equal(fileupload.filename, "test.data")
            assert_equal(fileupload.headers['content-type'],
                        "application/octet-stream")
            assert_equal(fileupload.file.read(), form_data.FILE_UPLOAD_DATA)

    def test_fileupload_too_big(self):
        """\
        Verify that multipart/form-data encoded POST data raises an exception
        if the total data size exceeds request.MAX_SIZE bytes
        """

        def view():
            request = context.request
            request.MAX_MULTIPART_SIZE = 500
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        r = TestAgent(app).post_multipart(
            files=[('f1', 'filename.txt', 'text/plain', 'x' * 1000)],
            check_status=False
        )
        assert_equal(r.response.status, "413 Request Entity Too Large")

        r = TestAgent(app).post_multipart(
            files=[('f1', 'filename.txt', 'text/plain', 'x' * 400)],
            data={'f2': 'x' * 101},
            check_status=False
        )
        assert_equal(r.response.status, "413 Request Entity Too Large")

    def test_fileupload_with_invalid_content_length(self):

        def view():
            request = context.request
            request.MAX_MULTIPART_SIZE = 500
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        r = TestAgent(app).post_multipart(
            files=[('f1', 'filename.txt', 'text/plain', 'x' * 1000)],
            CONTENT_LENGTH=unicode_to_environ("499"),
            check_status=False
        )
        assert_equal(r.response.status, "400 Bad Request")

    def test_multipart_field_too_big(self):
        """
        Verify that multipart/form-data encoded POST data raises an exception
        if it contains a single field exceeding request.MAX_SIZE bytes
        """
        def view():
            request = context.request
            request.MAX_MULTIPART_SIZE = 500
            request.MAX_SIZE = 100
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        r = TestAgent(app).post_multipart(data=[('f1', 'x' * 200)],
                                          check_status=False)
        assert_equal(r.response.status, "413 Request Entity Too Large")


class TestParseFormEncodedData(object):

    char_latin1 = b'\xa3'
    char_utf8 = b'\xc2\xa3'
    char = char_latin1.decode('latin1')

    assert char_latin1.decode('latin1') == char_utf8.decode('utf8') == char

    def test_formencoded_data_too_big(self):
        """
        Verify that application/x-www-form-urlencoded POST data raises an
        exception if it exceeds request.MAX_SIZE bytes
        """
        def view():
            request = context.request
            request.MAX_SIZE = 100
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        r = TestAgent(app).post(data=[('f1', 'x' * 200)], check_status=False)
        assert_equal(r.response.status, "413 Request Entity Too Large")

    def test_non_utf8_data_posted(self):

        data = b'char=' + quote(self.char_latin1).encode('ascii')
        env = {'REQUEST_METHOD': 'POST',
               'CONTENT_LENGTH': str(len(data)),
               'wsgi.input': BytesIO(data)}

        with FrescoApp().requestcontext(environ=env) as c:
            request = c.request
            request.charset = 'latin1'
            assert_equal(request.form['char'], self.char)

    def test_non_utf8_data_getted(self):

        data = 'char=' + quote(self.char_latin1)
        env = {'REQUEST_METHOD': 'GET', 'QUERY_STRING': data}

        with FrescoApp().requestcontext(environ=env) as c:
            request = c.request
            request.charset = 'latin1'
            assert_equal(request.query['char'], self.char)
