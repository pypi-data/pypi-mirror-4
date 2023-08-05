# coding=UTF-8

from io import BytesIO
from nose.tools import assert_equal

from fresco import FrescoApp
from fresco.compat import PY3, quote

context = FrescoApp().requestcontext


class TestRequestProperties(object):

    def test_url_script_name_only(self):
        with context(SCRIPT_NAME='/foo/bar', PATH_INFO='') as c:
            assert_equal(c.request.url, "http://localhost/foo/bar")

    def test_url_script_name_path_info(self):
        with context(SCRIPT_NAME='/foo/bar', PATH_INFO='/baz') as c:
            assert_equal(c.request.url, "http://localhost/foo/bar/baz")

    def test_url_normalizes_host_port(self):
        with context(HTTP_HOST='localhost:80') as c:
            assert_equal(c.request.url, "http://localhost/")
        with context(HTTP_HOST='localhost:81') as c:
            assert_equal(c.request.url, "http://localhost:81/")

    def test_url_normalizes_host_ssl_port(self):
        with context(environ={'wsgi.url_scheme': 'https'},
                     HTTP_HOST='localhost:443') as c:
            assert_equal(c.request.url, "https://localhost/")

    def test_url_ignores_server_port_if_host_header_present(self):
        with context(environ={'wsgi.url_scheme': 'https', 'SERVER_PORT': '81'},
                     HTTP_HOST='localhost') as c:
            assert_equal(c.request.url, "https://localhost/")

    def test_as_string(self):
        with context('http://example.org/foo?bar=baz') as c:
            assert_equal(str(c.request),
                         '<Request GET http://example.org/foo?bar=baz>')

    def test_url_returns_full_url(self):
        with context('http://example.org/foo?bar=baz') as c:
            assert_equal(c.request.url, 'http://example.org/foo?bar=baz')

    def test_path_returns_correct_path_when_script_name_empty(self):
        with context(SCRIPT_NAME='', PATH_INFO='/foo/bar') as c:
            assert_equal(c.request.path, '/foo/bar')

    def test_path_returns_correct_path(self):
        with context(SCRIPT_NAME='/foo', PATH_INFO='/bar') as c:
            assert_equal(c.request.path, '/foo/bar')


class TestPathEncoding(object):

    if PY3:
        unquoted_url = '/el niño'
        quoted_url = quote(unquoted_url)
        wsgi_url = unquoted_url.encode('utf8').decode('latin1')
    else:
        unquoted_url = unicode('/el niño', 'UTF-8')
        quoted_url = quote(unquoted_url.encode('UTF-8'))
        wsgi_url = unquoted_url.encode('UTF-8')

    def test_SCRIPT_NAME_PATH_INFO_latin1_decoded(self):

        with context(SCRIPT_NAME=self.unquoted_url,
                     PATH_INFO=self.unquoted_url) as c:
            assert c.request.environ['SCRIPT_NAME'] == self.wsgi_url
            assert c.request.environ['PATH_INFO'] == self.wsgi_url

    def test_url_is_quoted(self):

        with context(SCRIPT_NAME=self.unquoted_url, PATH_INFO='') as c:
            assert c.request.url == 'http://localhost' + self.quoted_url

    def test_application_url_is_quoted(self):

        with context(SCRIPT_NAME=self.unquoted_url, PATH_INFO='') as c:
            assert c.request.application_url == 'http://localhost' + \
                                                    self.quoted_url

    def test_parsed_url_is_quoted(self):
        with context(SCRIPT_NAME=self.unquoted_url, PATH_INFO='') as c:
            assert c.request.parsed_url.path == self.quoted_url

    def test_path_is_unquoted(self):
        with context(SCRIPT_NAME=self.unquoted_url, PATH_INFO='') as c:
            assert c.request.path == self.unquoted_url

    def test_script_name_is_unquoted(self):
        with context(SCRIPT_NAME=self.unquoted_url, PATH_INFO='') as c:
            assert c.request.script_name == self.unquoted_url

    def test_path_info_is_unquoted(self):
        with context(SCRIPT_NAME='', PATH_INFO=self.unquoted_url) as c:
            assert c.request.path_info == self.unquoted_url


class TestMakeURL(object):

    def test_returns_request_url(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.make_url(),
                         'http://localhost/script/pathinfo')

    def test_can_replace_path(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.make_url(path='/foo'),
                         'http://localhost/foo')

    def test_query_not_included_by_default(self):
        with context(QUERY_STRING='query=foo') as c:
            assert_equal(c.request.make_url(),
                         'http://localhost/')

    def test_query_dict(self):
        with context() as c:
            assert_equal(c.request.make_url(query={'a': 1, 'b': '2 3'}),
                         'http://localhost/?a=1;b=2+3')

    def test_query_kwargs(self):
        with context() as c:
            assert_equal(c.request.make_url(query={'a': 1}, b=2),
                         'http://localhost/?a=1;b=2')

    def test_unicode_path(self):
        e = b'\xc3\xa9'.decode('utf8')  # e-acute
        with context() as c:
            assert_equal(c.request.make_url(path=e),
                         'http://localhost/%C3%A9')

    def test_unicode_path_info(self):
        e = b'\xc3\xa9'.decode('utf8')  # e-acute
        with context() as c:
            assert_equal(c.request.make_url(PATH_INFO=e),
                         'http://localhost/%C3%A9')

    def test_unicode_query(self):
        e = b'\xc3\xa9'.decode('utf8')  # e-acute
        with context() as c:
            assert_equal(c.request.make_url(query={'e': e}),
                         'http://localhost/?e=%C3%A9')


class TestResolveURL(object):

    def test_relative_path(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.resolve_url('foo'),
                         'http://localhost/script/foo')

    def test_absolute_path_unspecified_relative(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.resolve_url('/foo', relative='app'),
                         'http://localhost/script/foo')

    def test_absolute_path_app_relative(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.resolve_url('/foo', relative='app'),
                         'http://localhost/script/foo')

    def test_absolute_path_server_relative(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.resolve_url('/foo', relative='server'),
                         'http://localhost/foo')

    def test_ignores_server_port_if_host_header_present(self):
        with context(environ={'wsgi.url_scheme': 'https', 'SERVER_PORT': '81'},
                     HTTP_HOST='localhost') as c:
            assert_equal(c.request.resolve_url('/foo'),
                         'https://localhost/foo')


class TestCurrentRequest(object):

    def test_currentrequest_returns_current_request(self):
        from fresco import currentrequest
        with context() as c:
            assert currentrequest() is c.request

    def test_currentrequest_returns_None(self):
        from fresco import currentrequest
        assert currentrequest() is None


class TestFiles(object):

    filename = 'test.txt'
    filedata = '123456\n'
    boundary = '---------------------------1234'

    post_data = (
        '--{boundary}\r\n'
        'Content-Disposition: form-data; '
            'name="uploaded_file"; filename="{filename}"\r\n'
        'Content-Type: text/plain\r\n'
        '\r\n'
        '{filedata}\r\n'
        '--{boundary}'
        '--\r\n'
    ).format(boundary=boundary, filedata=filedata, filename=filename)\
     .encode('latin1')

    request_args = {'wsgi_input': post_data,
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': 'multipart/form-data; boundary=' + \
                                        boundary,
                    'CONTENT_LENGTH': str(len(post_data))}

    def test_files_populated(self):

        with FrescoApp().requestcontext(**self.request_args) as c:
            request = c.request

        assert len(request.files) == 1
        assert 'uploaded_file' in request.files

    def test_file_content_available(self):

        with FrescoApp().requestcontext(**self.request_args) as c:
            request = c.request

        b = BytesIO()
        request.files['uploaded_file'].save(b)
        assert b.getvalue() == self.filedata.encode('latin1')

    def test_headers_available(self):

        with FrescoApp().requestcontext(**self.request_args) as c:
            request = c.request

        assert request.files['uploaded_file'].headers['content-type'] \
                == 'text/plain'
        assert request.files['uploaded_file'].filename == self.filename

#def test_parsing_cookie_header():
#    @to_wsgi
#    def app():
#        return Response([
#            str(cookie) + '\n' for name, cookie in request.cookies.allitems()
#        ])
#
#    assert_equal(
#        TestApp(app).get(HTTP_COOKIE='$Version=1; NAME=a; $Path="/"; $Domain=".some.domain.org"; NAME=b;').body,
#        "NAME=a;Domain=.some.domain.org;Path=/;Version=1\n"
#        "NAME=b;Version=1\n",
#    )
#
#
#def test_method_not_allowed_dispatcher():
#    dispatcher = dispatcher_app()
#
#    @dispatcher.match('/blah', 'DELETE', 'PUT')
#    def app():
#        return Response.method_not_allowed(request)
#
#    response = TestApp(dispatcher).get('/blah')
#    assert 'not allowed' in response.body.lower()
#    assert_equal(response.status, "405 Method Not Allowed")
#    assert_equal(response.get_header('Allow'), 'PUT,DELETE')
#

#def test_request_path():
#
#    request = Request(make_environ(SCRIPT_NAME='/foo', PATH_INFO='/bar', HTTP_HOST='localhost:80'))
#    assert_equal(request.request_path, "/foo/bar")
#
#    request = Request(make_environ(SCRIPT_NAME='/foo/bar', PATH_INFO='', HTTP_HOST='localhost:80'))
#    assert_equal(request.request_path, "/foo/bar")
#
#    request = Request(make_environ(SCRIPT_NAME='/', PATH_INFO='foo/bar', HTTP_HOST='localhost:80'))
#    assert_equal(request.request_path, "/foo/bar")
#
#def test_form():
#
#    request = Request(make_environ(QUERY_STRING='foo=bar'))
#    assert_equal(request.get('foo'), 'bar')
#    assert_equal(request['foo'], 'bar')
#    assert_equal(request.get('fuz'), None)
#
#    request = Request(make_environ(QUERY_STRING='foo=bar&foo=baz'))
#    assert_equal(request.get('foo'), 'bar')
#    assert_equal(request['foo'], 'bar')
#    assert_equal(request.getlist('foo'), ['bar', u'baz'])
#
#def test_remote_addr():
#    request = Request(make_environ(REMOTE_ADDR="1.2.3.4", HTTP_X_FORWARDED_FOR="4.3.2.1"))
#    assert request.remote_addr == "1.2.3.4"
#
#
#def test_encoding():
#
#    # Test UTF-8 decoding works (this should be the default)
#    request = Request(make_environ(QUERY_STRING=make_query(foo='\xa0'.encode('utf8'))))
#    assert_equal(request.get('foo'), '\xa0')
#
#    # Force a different encoding
#    request = Request(make_environ(QUERY_STRING=make_query(foo='\xa0'.encode('utf7'))))
#    request.charset = 'utf-7'
#    assert_equal(request.get('foo'), '\xa0')
#
#    # Force an incorrect encoding
#    request = Request(make_environ(QUERY_STRING=make_query(foo='\xa0'.encode('utf8'))))
#    request.charset = 'utf-7'
#    assert_raises(RequestParseError, request.get, 'foo')
#
#def test_form_getters():
#
#    alpha = '\u03b1' # Greek alpha
#    beta = '\u03b2' # Greek beta
#    gamma = '\u03b3' # Greek gamma
#
#    request = Request(make_environ(
#        QUERY_STRING='foo=%s;foo=%s;bar=%s' % (
#            quote(alpha.encode('utf-8')),
#            quote(beta.encode('utf-8')),
#            quote(gamma.encode('utf-8'))
#        )
#    ))
#    assert request.get('foo') == request.form.get('foo') == alpha
#    assert request.getlist('foo') == request.form.getlist('foo') == [alpha, beta]
#
#    assert request.get('cheese') == request.form.get('cheese') == None
#    assert request.getlist('cheese') == request.form.getlist('cheese') == []
#
#    assert request.get('bar') == request.form.get('bar') == gamma
#    assert request.getlist('bar') == request.form.getlist('bar') == [gamma]
#
#
