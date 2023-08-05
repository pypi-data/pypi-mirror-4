from functools import wraps
from mock import Mock
from nose.tools import assert_raises
from flea import TestAgent
from fresco import FrescoApp, GET, POST, Response
from fresco.exceptions import BadRequest, NotFound
from fresco.compat import ustring_type
from fresco.core import urlfor
from fresco.routing import Route, DelegateRoute, RouteCollection, \
                           RouteKwarg, CookieArg, SessionArg, FormArg, \
                           QueryArg, routefor
from . import fixtures


class TestMethodDispatch(object):

    def test_route_is_dispatched_to_correct_method(self):

        getview = Mock(return_value=Response(content_type='text/plain'))
        postview = Mock(return_value=Response(content_type='text/plain'))
        app = FrescoApp()
        app.route('/', GET, getview)
        app.route('/', POST, postview)

        TestAgent(app).get('/')
        assert getview.call_count == 1
        assert postview.call_count == 0

        TestAgent(app).post('/')
        assert getview.call_count == 1
        assert postview.call_count == 1


class TestRouteDecorators(object):

    def exclaim(self, func):
        @wraps(func)
        def exclaim(*args, **kwargs):
            response = func(*args, **kwargs)
            return response.replace(content=[''.join(response.content) + '!'])
        return exclaim

    def test_decorator_is_applied(self):

        views = fixtures.CBV('test')

        app = FrescoApp()
        app.route('/decorated', GET, views.index_html,
                  decorators=[self.exclaim])
        app.route('/plain', GET, views.index_html)

        with app.requestcontext('/decorated'):
            assert app.view().content == ['test!']

        with app.requestcontext('/plain'):
            assert app.view().content == ['test']

    def test_decorator_works_with_urlfor(self):

        views = fixtures.CBV('test')
        app = FrescoApp()
        app.route('/decorated', GET, views.index_html,
                  decorators=[self.exclaim])
        with app.requestcontext():
            assert urlfor(views.index_html, _app=app) == \
                    'http://localhost/decorated'

    def test_using_wraps_with_viewspec_doesnt_raise_AttributeError(self):

        def decorator(func):
            @wraps(func)
            def decorator(*args, **kwargs):
                return func(*args, **kwargs)
            return decorator

        class Views(object):
            __routes__ = Route('/',
                               GET, 'index_html', decorators=[decorator]),

            def index_html(self):
                return Response(['hello'])

        app = FrescoApp()
        app.include('/', Views())


class TestPredicates(object):

    def test_predicate_match(self):

        def v1():
            return Response(['x'])

        def v2():
            return Response(['y'])

        app = FrescoApp()
        app.route('/', GET, v1, predicate=lambda request: 'x' in request.query)
        app.route('/', GET, v2, predicate=lambda request: 'y' in request.query)

        t = TestAgent(app)
        assert t.get('/?x=1', check_status=False).body == 'x'
        assert t.get('/?y=1', check_status=False).body == 'y'
        assert t.get('/', check_status=False).response.status_code == 404


class TestRouteKwargs(object):

    def test_routekwarg_configured(self):

        A = RouteKwarg()
        route = Route('/', GET, lambda r: None, x=A)
        assert A.route is route
        assert A.name is 'x'

    def test_routekwarg_value_passed(self):

        view = Mock()
        routekwarg = Mock(spec=RouteKwarg)
        routekwarg.return_value = 'xyzzy'

        app = FrescoApp()
        app.route('/', GET, view, x=routekwarg)
        with app.requestcontext('/') as c:
            app.view()
            routekwarg.assert_called_with(c.request)
            view.assert_called_with(x='xyzzy')

    def test_queryarg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=QueryArg())
        with app.requestcontext('/?x=foo'):
            app.view()
            view.assert_called_with(x='foo')

    def test_formarg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=FormArg())
        with app.requestcontext('/?x=foo'):
            app.view()
            view.assert_called_with(x='foo')

    def test_sessionarg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=SessionArg())
        with app.requestcontext('/?x=foo') as c:
            c.request.environ[c.request.SESSION_ENV_KEY] = {'x': 'foo'}
            app.view()
            view.assert_called_with(x='foo')

    def test_cookiearg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=CookieArg())
        with app.requestcontext('/', HTTP_COOKIE='x=foo'):
            app.view()
            view.assert_called_with(x='foo')

    def test_cookiearg_listvalue_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=CookieArg([str]))
        with app.requestcontext('/', HTTP_COOKIE='x=foo;x=bar'):
            app.view()
            view.assert_called_with(x=['foo', 'bar'])

    def test_requestarg_value_converted(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=FormArg(float))
        with app.requestcontext('/?x=0'):
            app.view()
            view.assert_called_with(x=0.0)

    def test_requestarg_default_value(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=FormArg(default='d'))
        with app.requestcontext('/'):
            app.view()
            view.assert_called_with(x='d')

    def test_requestarg_returns_badrequest(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=FormArg())
        with app.requestcontext('/'):
            assert 'Bad Request' in app.view().status


class TestRouteNames(object):

    def test_name_present_in_route_keys(self):
        r = Route('/', GET, None, name='foo')
        assert 'foo' in list(r.route_keys())

    def test_name_with_other_kwargs(self):
        r = Route('/', GET, None, name='foo', x='bar')
        assert 'foo' in list(r.route_keys())

    def test_name_cannot_contain_colon(self):
        assert_raises(ValueError, Route, '/', GET, None, name='foo:bar')


class TestRouteCollection(object):

    def test_get_routes_matches_on_method(self):

        r_get = Route('/', GET, None)
        r_post = Route('/', POST, None)

        rc = RouteCollection([r_post, r_get])

        assert [r.route for r in rc.get_routes('/', GET)] == [r_get]
        assert [r.route for r in rc.get_routes('/', POST)] == [r_post]

    def test_get_routes_matches_on_path(self):

        r1 = Route('/1', GET, None)
        r2 = Route('/2', GET, None)

        rc = RouteCollection([r1, r2])

        assert [r.route for r in rc.get_routes('/1', GET)] == [r1]
        assert [r.route for r in rc.get_routes('/2', GET)] == [r2]

    def test_get_routes_can_match_all_methods(self):

        r1 = Route('/1', GET, None)
        r2 = Route('/1', POST, None)

        rc = RouteCollection([r1, r2])
        assert [r.route for r in rc.get_routes('/1', None)] == [r1, r2]

    def test_route_returns_traversal_information_on_nested_routes(self):

        a = RouteCollection()
        b = RouteCollection()

        a.route('/harvey', GET, lambda: None)
        b.route('/harvey', GET, lambda: None)

        a.delegate('/rabbit', b)
        b.delegate('/hole', a)

        r = next(a.get_routes('/rabbit/hole/rabbit/harvey', None))
        assert r.collections_traversed == [(a, ''),
                                           (b, '/rabbit'),
                                           (a, '/rabbit/hole'),
                                           (b, '/rabbit/hole/rabbit')]


class TestRoutefor(object):

    def test_routefor_with_view_function(self):

        def view():
            return Response(['ok'])

        app = FrescoApp()
        route = app.route('/foo', GET, view)

        with app.requestcontext():
            assert routefor(view) == route

    def test_routefor_with_string(self):
        app = FrescoApp()
        route = app.route('/myviewfunc', GET, fixtures.module_level_function)
        with app.requestcontext():
            assert routefor('fresco.tests.fixtures.module_level_function') == \
                    route

    def test_routefor_generates_first_route(self):

        myviewfunc = lambda req: Response([])
        app = FrescoApp()
        r1 = app.route('/1', GET, myviewfunc)
        app.route('/2', GET, myviewfunc)
        with app.requestcontext():
            assert routefor(myviewfunc) == r1


class TestDelegatedRoutes(object):

    def test_dispatch_to_delegated_route(self):

        def hello():
            return Response(['hello'])

        inner = FrescoApp()
        inner.route('/hello', GET, hello)

        outer = FrescoApp()
        outer.delegate('/say', inner)

        r = TestAgent(outer).get('/say/hello')
        assert r.body == 'hello'

    def test_url_variables_are_passed(self):

        hello = Mock()

        inner = FrescoApp()
        inner.route('/<i:str>', GET, hello)

        outer = FrescoApp()
        outer.delegate('/<o:str>', inner)

        with outer.requestcontext('/foo/bar'):
            outer.view()
            hello.assert_called_with(i='bar', o='foo')

    def test_delegation_to_dynamic_routes(self):

        result = []

        class MyRoutes(object):
            __routes__ = [Route('/<inner:int>/view', GET, 'view')]

            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def view(self, **kwargs):
                result.append((self, kwargs))

        app = FrescoApp()
        app.delegate('/<outer:str>', MyRoutes, dynamic=True)
        with app.requestcontext('/two/2/view'):
            app.view()
            instance, inner_kwargs = result[0]
            assert inner_kwargs == {'inner': 2}
            assert instance.kwargs == {'outer': 'two'}

    def test_pathfor_with_delegated_route(self):
        inner = FrescoApp()
        inner.route('/<i:str>', GET, lambda: None, name='inner-route')

        outer = FrescoApp()
        outer.delegate('/<o:str>', inner, name='delegation')

        with outer.requestcontext('/foo/bar'):
            assert outer.pathfor('delegation:inner-route',
                                o='x', i='y') == '/x/y'

    def test_pathfor_with_dynamic_delegated_route(self):

        view = Mock()

        def routecollectionfactory(*args, **kwargs):
            return RouteCollection([Route('/<i:str>', GET, view,
                                          name='inner-route')])

        rc = RouteCollection()
        rc.delegate('/<o:str>', routecollectionfactory,
                     name='delegation', dynamic=True)

        assert rc.pathfor('delegation:inner-route', o='x', i='y') == '/x/y'

    def test_urlfor_with_dynamic_delegated_route_and_view_self(self):

        result = []

        class MyRoutes(object):
            __routes__ = [Route('/<inner:int>/view', GET, 'view')]

            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def view(self, **kwargs):
                result.append(urlfor(self.view, inner=3))

        app = FrescoApp()
        app.delegate('/<outer:str>', MyRoutes, dynamic=True)
        with app.requestcontext('/two/2/view'):
            app.view()
            assert result == ['http://localhost/two/3/view']

    def test_urlgeneration_with_dynamic_routes(self):

        class Routable(object):
            __routes__ = [Route('/<b:int>', GET, 'view', name='y')]

            def __init__(self, a):
                pass

            def view(self, b):
                pass

        app = FrescoApp()
        app.delegate('/<a:str>', Routable, dynamic=True, name='x')
        with app.requestcontext('/two/2/view'):
            assert urlfor('x:y', a='a', b=1) == 'http://localhost/a/1'

    def test_delegated_routes_can_be_included(self):

        view = Mock()

        inner = RouteCollection([Route('/baz', GET, view)])
        middle = RouteCollection([DelegateRoute('/bar', inner)])
        outer = FrescoApp()
        outer.include('/foo', middle)
        with outer.requestcontext('/foo/bar/baz'):
            outer.view()
            view.assert_called()

    def test_not_found_is_returned(self):

        def inner():
            raise NotFound()

        outer = FrescoApp()
        outer.delegate('/foo', inner, dynamic=True)
        with outer.requestcontext('/foo/bar/baz'):
            response = outer.view()
            assert response.status_code == 404

    def test_not_found_causes_next_route_to_be_tried(self):

        def inner():
            raise NotFound()
        view = Mock()

        outer = FrescoApp()
        outer.delegate('/foo', inner, dynamic=True)
        outer.route('/foo', view)
        with outer.requestcontext('/foo'):
            outer.view()
            view.assert_called()


class TestConverters(object):

    def test_str_converter_returns_unicode(self):
        from fresco.routing import StrConverter
        s = ustring_type('abc')
        assert isinstance(StrConverter().from_string(s), ustring_type)
