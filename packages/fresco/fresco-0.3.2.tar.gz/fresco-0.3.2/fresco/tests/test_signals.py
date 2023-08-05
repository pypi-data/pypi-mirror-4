from flea import TestAgent
from fresco import FrescoApp, GET, Response


class Receiver(object):

    def __init__(self):
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))


class TestSignals(object):

    def test_route_matched_is_fired(self):

        def view():
            return Response([])

        app = FrescoApp()
        app.route('/0', GET, view)
        app.route('/1', GET, view)

        receiver = Receiver()
        app.route_matched.connect(receiver)

        TestAgent(app).get('/0')
        TestAgent(app).get('/1')

        assert len(receiver.calls) == 2

        args, kwargs = receiver.calls[0]
        assert args[0] is app
        assert kwargs.pop('route') is app.__routes__[0]
        assert kwargs.pop('view') is view
        assert kwargs.pop('request').path == '/0'
        assert kwargs == {}

        args, kwargs = receiver.calls[1]
        assert args[0] is app
        assert kwargs.pop('route') is app.__routes__[1]
        assert kwargs.pop('view') is view
        assert kwargs.pop('request').path == '/1'
        assert kwargs == {}

    def test_view_finished_is_fired(self):

        def view():
            return Response(['xyzzy'])

        app = FrescoApp()
        app.route('/', GET, view)

        receiver = Receiver()
        app.view_finished.connect(receiver)

        TestAgent(app).get('/')

        assert len(receiver.calls) == 1

        args, kwargs = receiver.calls[0]
        assert args[0] is app
        assert kwargs.pop('view') is view
        assert kwargs.pop('response').content == ['xyzzy']
        assert kwargs == {}

    def test_signals_isolated(self):
        def view():
            return Response(['xyzzy'])

        app1 = FrescoApp()
        app1.route('/', GET, view)

        app2 = FrescoApp()
        app2.route('/', GET, view)

        receiver1 = Receiver()
        receiver2 = Receiver()
        app1.route_matched.connect(receiver1)
        app2.route_matched.connect(receiver2)

        TestAgent(app1).get('/')
        assert len(receiver1.calls) == 1
        assert len(receiver2.calls) == 0
        TestAgent(app2).get('/')
        assert len(receiver1.calls) == 1
        assert len(receiver2.calls) == 1
