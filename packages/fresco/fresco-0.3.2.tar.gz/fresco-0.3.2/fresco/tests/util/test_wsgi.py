from nose.tools import assert_equal
from flea import TestAgent
from fresco.util.wsgi import ClosingIterator, StartResponseWrapper


class Counter(object):

    value = 0

    def inc(self):
        self.value += 1


def start_response(status, headers, exc_info=None):
    pass


class _TestException(Exception):
    pass


class TestClosingIterator(object):

    def app(self, environ, start_response):
        start_response('200 OK', [('Content-Type: text/plain')])
        yield "Foo"
        yield "Bar"

    def test_close_called_after_iterator_finished(self):
        count = Counter()
        environ = {}

        result = self.app(environ, start_response)
        result = ClosingIterator(result, count.inc)
        assert_equal(count.value, 0)
        try:
            list(result)
        finally:
            result.close()
        assert_equal(count.value, 1)

    def test_multiple_close_functions_called(self):
        count1 = Counter()
        count2 = Counter()
        environ = {}

        result = self.app(environ, start_response)
        result = ClosingIterator(result, count1.inc, count2.inc)
        assert_equal(count1.value, 0)
        assert_equal(count2.value, 0)
        try:
            list(result)
        finally:
            result.close()
        assert_equal(count1.value, 1)
        assert_equal(count2.value, 1)


class TestStartResponseWrapper(object):

    def test_write(self):

        def wsgiapp(environ, start_response):
            start_response = StartResponseWrapper(start_response)
            write = start_response('200 OK', [('Content-Type', 'text/plain')])

            write(b'cat')
            write(b'sat')
            write2 = start_response.call_start_response()
            write2(b'mat')
            return []

        assert_equal(TestAgent(wsgiapp).get('/').body, 'catsatmat')
