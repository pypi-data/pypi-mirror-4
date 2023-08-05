from flea import TestAgent
from nose.tools import assert_equal, assert_raises

from fresco import FrescoApp, GET, Response
from fresco.decorators import extract_getargs
from fresco.exceptions import BadRequest

class TestExtractGetArgs(object):

    def test_mixed_with_dispatcher_args(self):

        app = FrescoApp()

        @app.route(r'/<arg1:str>/<arg2:str>', GET)
        @extract_getargs(arg1=str, arg2=int)
        def handler(arg1, arg2):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__, arg2, type(arg2).__name__)
            ])

        assert_equal(
            TestAgent(app).get('/foo/29').body,
            "Received 'foo':str, 29:int"
        )

    def test_query_args(self):

        @extract_getargs(arg1=str, arg2=int)
        def view(arg1, arg2):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__, arg2, type(arg2).__name__)
            ])

        app = FrescoApp()
        app.route('/', GET, view)
        assert_equal(
            TestAgent(app).get('/?arg1=foo;arg2=29').body,
            "Received 'foo':str, 29:int"
        )

    def test_missing_args_with_one_default_argument(self):

        @extract_getargs(arg1=str, arg2=int)
        def view(arg1, arg2):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__, arg2, type(arg2).__name__)
            ])

        app = FrescoApp()
        app.route('/', GET, view)
        assert_equal(
            TestAgent(app).get('/?arg1=foo', check_status=False).response.status_code,
            400
        )

    def test_missing_args(self):

        @extract_getargs(arg1=str, arg2=int)
        def view(arg1, arg2=None):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__, arg2, type(arg2).__name__)
            ])

        app = FrescoApp()
        app.route('/', GET, view)
        r = TestAgent(app).get('/?arg1=foo')
        assert_equal(r.response.status, '200 OK')
        assert_equal(r.body, "Received 'foo':str, None:NoneType")

    def test_conversion_error_without_default(self):

        @extract_getargs(arg1=int)
        def view(arg1):
            return Response([])

        app = FrescoApp()
        app.route('/', GET, view)
        assert_equal(TestAgent(app).get('/?arg1=foo', check_status=False).response.status_code, 400)

    def test_conversion_error_with_strict_checking(self):

        @extract_getargs(arg1=int, strict_checking=True)
        def view(arg1=None):
            return Response([
                'Received %r:%s' % (arg1, type(arg1).__name__)
            ])

        app = FrescoApp()
        app.route('/', GET, view)
        assert_equal(TestAgent(app).get('/?arg1=foo', check_status=False).response.status_code, 400)

    def test_no_conversion_error_with_default(self):

        @extract_getargs(arg1=int)
        def view(arg1=None):
            return Response([
                'Received %r:%s' % (arg1, type(arg1).__name__)
            ])

        app = FrescoApp()
        app.route('/', GET, view)
        assert_equal(TestAgent(app).get('/?arg1=foo').body, 'Received None:NoneType')

