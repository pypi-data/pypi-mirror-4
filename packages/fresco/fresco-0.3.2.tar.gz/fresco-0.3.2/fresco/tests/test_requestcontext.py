from flea import TestAgent
from nose.tools import assert_equal, assert_raises

from fresco import FrescoApp, GET, Response
from fresco.requestcontext import RequestContext

class TestRequestContext(object):

    def test_instantiation(self):
        """
        Can we cleanly instantiate a RequestContext object?
        """
        s = RequestContext()

    def test_app_populates_request_object(self):

        def view():
            from fresco.core import context
            assert context.request is not None
            return Response([''])

        app = FrescoApp()
        app.route('/', GET, view)

        assert_equal(TestAgent(app).get('/').body, '')

    def test_context_returns_correct_request_for_each_app(self):

        from time import sleep
        from threading import Thread, Lock, current_thread
        from functools import partial

        threadcount = 3
        itercount = 10
        output = []
        output_lock = Lock()

        def view():
            from fresco.core import context
            request_id = id(context.request)
            def generate_response():
                for i in range(itercount):
                    assert id(context.request) == request_id
                    output_lock.acquire()
                    output.append((request_id, current_thread(), i))
                    output_lock.release()
                    sleep(0.001)
                    yield str(request_id).encode('ascii')
            return Response(generate_response())

        app = FrescoApp()
        app.route('/', GET, view)

        threads = [Thread(target=partial(TestAgent(app).get, '/'))
                   for i in range(threadcount)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Check that threaded requests were genuinely interleaved
        for i1, i2 in zip(output[:itercount-1], output[1:itercount]):
            if i1[:2] != i2[:2]:
                break
        else:
            raise AssertionError("Output does not appear interleaved")
        assert_equal(len(output), threadcount * itercount)


    def test_context_inherits_from_parent(self):
        c = RequestContext()
        c.push(foo=1)
        c.push(bar=2)
        assert_equal(c.foo, 1)

    def test_child_context_overrides_parent(self):
        c = RequestContext()
        c.push(foo=1)
        c.push(foo=2)
        assert_equal(c.foo, 2)

    def test_pop_context_removes_keys(self):
        c = RequestContext()
        c.push(foo=1)
        c.push(foo=2)
        assert_equal(c.foo, 2)
        c.pop()
        assert_equal(c.foo, 1)

