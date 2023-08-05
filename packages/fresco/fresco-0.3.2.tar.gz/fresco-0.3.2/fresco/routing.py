import re
import sys
from collections import namedtuple
from functools import partial
from itertools import cycle
from operator import attrgetter, itemgetter, methodcaller

from fresco.compat import string_types
from fresco.exceptions import BadRequest, ResponseException
from fresco.response import Response
from fresco.requestcontext import context
from fresco.util.urls import join_path

HTTP_METHODS = GET, HEAD, POST, PUT, DELETE = \
               'GET', 'HEAD', 'POST', 'PUT', 'DELETE'

ALL_METHODS = HTTP_METHODS


__all__ = HTTP_METHODS + ('ALL_METHODS', 'Pattern', 'Route', 'DelegateRoute',
                          'RouteCollection', 'FormArg', 'QueryArg',
                          'CookieArg', 'routefor')


#: Encapsulate a pattern match on a path
PathMatch = namedtuple('PathMatch', ['path_matched', 'path_remaining',
                                     'args', 'kwargs'])

#: Encapsulate a route traversal
RouteTraversal = namedtuple('RouteTraversal',
                            ['route', 'args', 'kwargs',
                             'collections_traversed'])


class URLGenerationError(Exception):
    """\
    Was not possible to generate the requested URL.
    """


class RouteNotFound(Exception):
    """\
    The named route does not exist in the RouteCollection.
    """


class Pattern(object):
    """\
    Patterns are matchable against URL paths using their ``match`` method. If a
    path matches, this should return a tuple of ``(positional_arguments,
    keyword_arguments)`` extracted from the URL path. Otherwise this method
    should return ``None``.

    Pattern objects may also be able to take a tuple of
    ``(positional_arguments, keyword_arguments)`` and return a corresponding
    URL path.
    """

    def match(self, path):
        """
        Should return a tuple of ``(positional_arguments, keyword_arguments)``
        if the pattern matches the given URL path, or None if it does not
        match.
        """
        raise NotImplementedError

    def pathfor(self, *args, **kwargs):
        """
        The inverse of ``match``, this should return a URL path
        for the given positional and keyword arguments, along with any unused
        arguments.

        :return: a tuple of ``(path, remaining_args, remaining_kwargs)``
        """
        raise NotImplementedError()

    def add_prefix(self, prefix):
        """
        Return a copy of the pattern with the given string prepended
        """
        raise NotImplementedError()


class Converter(object):
    """\
    Responsible for converting arguments to and from URL components.

    A ``Converter`` class should provide two instance methods:

    - ``to_string``: convert from a python object to a string
    - ``from_string``: convert from URL-encoded bytestring to the target
                        python type.

    It must also define the regular expression pattern that is used to extract
    the string from the URL.
    """
    pattern = '[^/]+'

    def __init__(self, pattern=None):
        """
        Initialize a ``Converter`` instance.
        """
        if pattern is not None:
            self.pattern = pattern

    def to_string(self, ob):
        """
        Convert arbitrary argument ``ob`` to a string representation
        """
        return str(ob)

    def from_string(self, s):
        """
        Convert string argument ``a`` to the target object representation,
        whatever that may be.
        """
        raise NotImplementedError


class IntConverter(Converter):
    """\
    Match any integer value and convert to an ``int`` value.
    """

    pattern = r'[+-]?\d+'

    def from_string(self, s):
        """
        Return ``s`` converted to an ``int`` value.
        """
        return int(s)


class StrConverter(Converter):
    """\
    Match any string, not including a forward slash, and return a ``str``
    value
    """

    pattern = r'[^/]+'

    def to_string(self, s):
        """
        Return ``s`` converted to an ``str`` object.
        """
        return s

    def from_string(self, s):
        """
        Return ``s`` converted to a (unicode) string type
        """
        return s


class AnyConverter(StrConverter):
    """
    Match any one of the given string options.
    """

    pattern = r'[+-]?\d+'

    def __init__(self, *args):
        super(AnyConverter, self).__init__(None)
        if len(args) == 0:
            raise ValueError("Must supply at least one argument to any()")
        self.pattern = '|'.join(re.escape(arg) for arg in args)


class PathConverter(StrConverter):
    """\
    Match any string, possibly including forward slashes, and return a
    ``str`` object.
    """
    pattern = r'.+'


class MatchAllURLsPattern(Pattern):
    """\
    A pattern matcher that matches all URLs starting with the given prefix. No
    arguments are parsed from the URL.
    """

    def __init__(self, path):
        self.path = path

    def match(self, path):
        if path.startswith(self.path):
            return PathMatch(self.path, path[len(self.path):], (), {})
        return None

    def pathfor(self, *args, **kwargs):
        assert not args and not kwargs, \
                "MatchAllURLsPattern does not support URL arguments"

        return self.path, (), {}

    def add_prefix(self, prefix):
        return self.__class__(join_path(prefix, self.path))

    def __str__(self):
        return '%s*' % (self.path,)


class ExtensiblePattern(Pattern):
    """\
    An extensible URL pattern matcher.

    Synopsis::

        >>> from pprint import pprint
        >>> p = ExtensiblePattern(r"/<:str>/<year:int>/<title:str>")
        >>> pprint(p.match('/archive/1999/blah'))
        (('archive',), {'title': 'blah', 'year': 1999})

    Patterns are split on slashes into components. A component can either be a
    literal part of the path, or a pattern component in the form::

        <identifier>:<converter>

    ``identifer`` can be any python name, which will be used as the name of a
    keyword argument to the matched function. If omitted, the argument will be
    passed as a positional arg.

    ``converter`` must be the name of a pre-registered converter. Converters
    must support ``to_string`` and ``from_string`` methods and are used to
    convert between URL segments and python objects.

    By default, the following converters are configured:

    - ``int`` - converts to an integer
    - ``path`` - any path (ie can include forward slashes)
    - ``str`` - any string (not including forward slashes)
    - ``unicode`` - alias for ``str``
    - ``any`` - a string matching a list of alternatives

    Some examples::

        >>> p = ExtensiblePattern(r"/images/<:path>")
        >>> p.match('/images/thumbnails/02.jpg')
        (('thumbnails/02.jpg',), {})

        >>> p = ExtensiblePattern("/<page:any('about', 'help')>.html")
        >>> p.match('/about.html')
        ((), {'page': 'about'})

        >>> p = ExtensiblePattern("/entries/<id:int>")
        >>> p.match('/entries/23')
        ((), {'id': 23})

    Others can be added by calling ``ExtensiblePattern.register_converter``
    """

    preset_patterns = (
        ('int', IntConverter),
        ('str', StrConverter),
        ('unicode', StrConverter),
        ('path', PathConverter),
        ('any', AnyConverter),
    )
    pattern_parser = re.compile("""
        <
            (?P<name>\w[\w\d]*)?
            :
            (?P<converter>\w[\w\d]*)
            (?:
                \(
                         (?P<args>.*?)
                \)
            )?
        >
    """, re.X)

    class Segment(object):
        """
        Represent a single segment of a URL, storing information about hte
        ``source``, ``regex`` used to pattern match the segment, ``name`` for
        named parameters and the ``converter`` used to map the value to a URL
        parameter if applicable
        """

        def __init__(self, source, regex, name, converter):
            self.source = source
            self.regex = regex
            self.name = name
            self.converter = converter

    def __init__(self, pattern, match_entire_path=True):
        """
        Initialize a new ``ExtensiblePattern`` object with pattern ``pattern``

        :param pattern: The pattern string, eg ``'/<id:int>/show'``
        :param match_entire_path: Boolean. If ``True``, the entire path will be
                                  required to match, otherwise a prefix match
                                  will suffice.
        """
        super(ExtensiblePattern, self).__init__()

        self.preset_patterns = dict(self.preset_patterns)
        self.pattern = pattern
        self.match_entire_path = match_entire_path

        self.segments = list(self._make_segments(pattern))
        self.args = [item
                     for item in self.segments
                     if item.converter is not None]

        regex = ''.join(segment.regex for segment in self.segments)
        if self.match_entire_path:
            regex += '$'

        self.regex = re.compile(regex)

    def _make_segments(self, s):
        r"""
        Generate successive Segment objects from the given string.

        Each segment object represents a part of the pattern to be matched, and
        comprises ``source``, ``regex``, ``name`` (if a named parameter) and
        ``converter`` (if a parameter)
        """

        for item in split_iter(self.pattern_parser, self.pattern):
            if isinstance(item, string_types):
                yield self.Segment(item, re.escape(item), None, None)
                continue
            groups = item.groupdict()
            name, converter, args = (groups['name'], groups['converter'],
                                     groups['args'])
            converter = self.preset_patterns[converter]
            if args:
                args, kwargs = self.parseargs(args)
                converter = converter(*args, **kwargs)
            else:
                converter = converter()
            yield self.Segment(item.group(0),
                               '(%s)' % converter.pattern, name, converter)

    def parseargs(self, argstr):
        """
        Return a tuple of ``(args, kwargs)`` parsed out of a string in the
        format ``arg1, arg2, param=arg3``.

        Synopsis::

            >>> ep =  ExtensiblePattern('')
            >>> ep.parseargs("1, 2, 'buckle my shoe'")
            ((1, 2, 'buckle my shoe'), {})
            >>> ep.parseargs("3, four='knock on the door'")
            ((3,), {'four': 'knock on the door'})

        """
        return eval('(lambda *args, **kwargs: (args, kwargs))(%s)' % argstr)

    def match(self, path):
        """
        Test ``path`` and return a tuple of parsed ``(args, kwargs)``, or
        ``None`` if there was no match.
        """
        mo = self.regex.match(path)
        if not mo:
            return None
        groups = mo.groups()
        assert len(groups) == len(self.args), (
                "Number of regex groups does not match expected count. "
                "Perhaps you have used capturing parentheses somewhere? "
                "The pattern matched was %r." % self.regex.pattern
        )

        try:
            groups = [
                (segment.name, segment.converter.from_string(value))
                  for value, segment in zip(groups, self.args)
            ]
        except ValueError:
            return None

        args = tuple(value for name, value in groups if not name)
        kwargs = dict((name, value) for name, value in groups if name)
        return PathMatch(mo.group(0), path[len(mo.group(0)):], args, kwargs)

    def pathfor(self, *args, **kwargs):
        """
        Example usage::

            >>> p = ExtensiblePattern("/view/<name:str>/<revision:int>")
            >>> p.pathfor(name='important_document.pdf', revision=299)
            '/view/important_document.pdf/299'

            >>> p = ExtensiblePattern("/view/<:str>/<:int>")
            >>> p.pathfor('important_document.pdf', 299)
            '/view/important_document.pdf/299'
        """

        args = list(args)
        kwargs = kwargs
        result = []
        for seg in self.segments:
            if not seg.converter:
                result.append(seg.source)
            elif seg.name:
                try:
                    result.append(seg.converter.to_string(
                                                    kwargs.pop(seg.name)))
                except IndexError:
                    raise URLGenerationError(
                        "Argument %r not specified for url %r" % (
                            seg.name, self.pattern
                        )
                    )
            else:
                try:
                    result.append(seg.converter.to_string(args.pop(0)))
                except IndexError:
                    raise URLGenerationError(
                        "Not enough positional arguments for url %r" % (
                            self.pattern,
                        )
                    )
        return ''.join(result), args, kwargs

    def add_prefix(self, prefix):
        return self.__class__(join_path(prefix, self.pattern))

    @classmethod
    def register_converter(cls, name, converter):
        """
        Register a preset pattern for later use in URL patterns.

        Example usage::

            >>> from datetime import date
            >>> from time import strptime
            >>> class DateConverter(Converter):
            ...     pattern = r'\d{8}'
            ...     def from_string(self, s):
            ...         return date(*strptime(s, '%d%m%Y')[:3])
            ...
            >>> ExtensiblePattern.register_converter('date', DateConverter)
            >>> ExtensiblePattern('/<:date>').match('/01011970')
            ((datetime.date(1970, 1, 1),), {})
        """
        cls.preset_patterns += ((name, converter),)

    def __repr__(self):
        return '<%s %r>' % (self.__class__, self.pattern)

    def __str__(self):
        return '%s' % (self.pattern,)


class Route(object):
    """\
    Represent a URL routing pattern
    """

    #: The default class to use for URL pattern matching
    pattern_class = ExtensiblePattern

    def __init__(self, pattern, methods, view, view_kwargs=None,
                 name=None, predicate=None, decorators=None, **kwargs):

        """
        :param pattern:     A string that can be compiled into a path pattern
        :param methods:     The list of HTTP methods the view is bound to
                            ('GET', 'POST', etc)
        :param view:        The view function.
        :param view_kwargs: A dictionary of default keyword arguments to pass
                            to the view callable
        :param name:        A name that can later be used to retrieve the route
                            for URL generation
        :param predicate:   A callable that is used to decide whether to match
                            this pattern. The callable must take a ``Request``
                            object as its only parameter and return a boolean.
        :param decorators:  Decorator functions to apply to the view callable
                            before invoking it
        :param kwargs:      Other keyword aruments passed through to the view
                            callable.


        Naming routes
        -------------

        Naming routes allows you to reference routes throughout your
        application, eg when generating URLs with
        :function:`~fresco.core.urlfor`.

        If you don't specify a ``name`` argument, the route will available by
        its fully qualified function name (eg
        ``'package.module.view_function'``), or by passing the function object
        itself to ``urlfor``

        Views may often be assigned to multiple routes, for example::

            Route('/image', display_image, size=(1024, 768))
            Route('/thumbnail', display_image, size=(75, 75))

        If you generate a URL for the view function ``display_image``, the
        the first declared route will always win, in this case::

            >>> urlfor(display_image)
            'http://localhost/image'

        To generate URLs for the thumbnail route in this example, you must
        explicity assign names::

            Route('/image', display_image, name='image', ...)
            Route('/thumbnail', display_image, name='image-thumbnail', ...)

            >> urlfor('image')
            'http://localhost/image'
            >> urlfor('image-thumbnail')
            'http://localhost/thumbnail'

        """

        if isinstance(methods, string_types):
            methods = [methods]
        else:
            # Catch the common error of not providing a valid method
            try:
                methods = set(methods)
            except TypeError:
                raise TypeError("Methods must be a string or iterable")

        if not isinstance(pattern, Pattern):
            pattern = self.pattern_class(pattern)

        if name and ':' in name:
            # Colons are reserved to act as separators
            raise ValueError("Route names cannot contain ':'")

        self.pattern = pattern
        self.methods = set(methods)
        self.view_kwargs = dict(view_kwargs or {}, **kwargs)
        for argname, arg in self.view_kwargs.items():
            if isinstance(arg, RouteKwarg):
                arg.configure(self, argname)

        self.name = name
        self.predicate = predicate
        self.decorators = decorators or []
        self.set_view(view)

    def __str__(self):
        return '%s %s => %r\n' % (
            ' '.join(self.methods),
            str(self.pattern),
            self.original_view
        )

    def __repr__(self):
        return '<%s %s %r %s>' % (
            self.__class__.__name__,
            ','.join(self.methods),
            str(self.pattern),
            self.original_view
        )

    def match(self, path, method):
        if method and method not in self.methods:
            return None
        return self.pattern.match(path)

    def set_view(self, view):
        decorated_view = view
        if not isinstance(view, string_types):
            for d in (self.decorators or []):
                decorated_view = d(decorated_view)

        self.original_view = view
        self.view = decorated_view

    def resolve_view(self, instance):
        """
        Resolve a view spec string to the actual callable.
        """
        if isinstance(self.original_view, string_types):
            self.set_view(getattr(instance, self.original_view))

    def add_prefix(self, path):
        """
        Return a copy of the Route object with the given path prepended to the
        routing pattern.
        """
        newroute = object.__new__(self.__class__)
        newroute.__dict__ = dict(self.__dict__,
                                 pattern=self.pattern.add_prefix(path))
        return newroute

    def path(self, *args, **kwargs):
        """\
        Return a tuple of URL path component corresponding to the route and
        remaining positional and keyword arguments

        Positional and keywords arguments are forwarded to the ``pathfor``
        method of the pattern.
        """
        return self.pattern.pathfor(*args, **kwargs)

    def route_keys(self):
        """\
        Generate keys by which the route should be indexed
        """
        if self.name:
            yield self.name
        yield self.original_view

        # Also return the underlying function object for python2 unbound
        # methods
        func_ob = getattr(self.original_view, '__func__', None)
        if func_ob is not None:
            yield func_ob


def split_iter(pattern, string):
    """
    Generate alternate strings and match objects for all occurances of
    ``pattern`` in ``string``.
    """
    matcher = pattern.finditer(string)
    match = None
    pos = 0
    for match in matcher:
        yield string[pos:match.start()]
        yield match
        pos = match.end()
    yield string[pos:]


def routefor(viewspec, _app=None):
    """\
    Convenience wrapper around :meth:`~fresco.routing.RouteCollection.urlfor`.
    """
    return context.app.routefor(viewspec)


class RouteCollection(object):
    """\
    A collection of :class:`~fresco.routing.Route` objects, RouteCollections:

    - Contain methods to configure routes, including the ability to
      delegate URLs to other RouteCollections
    - Can map from a request to a view
    """

    def __init__(self, routes=None):
        self.__routes__ = []
        self.__routed_views__ = {}
        if routes:
            for item in routes:
                self.add_route(item)

    def add_route(self, route):
        self.__routes__.append(route)

        for item in route.route_keys():
            if item not in self.__routed_views__:
                self.__routed_views__[item] = route

        self._add_url_method(route.original_view, route)

    def _add_url_method(self, func, route):
        """\
        Add a method available at ``func.url`` that returns a URL generated
        from the given route
        """
        from fresco.core import urlfor
        if hasattr(func, 'url'):
            return
        try:
            func.url = partial(urlfor, func)
        except AttributeError:
            # Cannot set function attributes on bound or unbound methods.
            # See http://www.python.org/dev/peps/pep-0232/
            pass

    def pathfor(self, viewspec, *args, **kwargs):
        """\
        Return the path component of the url for the given view name/function
        spec.

        :param viewspec: a view name, a reference in the form
                         ``'package.module.viewfunction'``, or the view
                         callable itself.
        """
        if isinstance(viewspec, string_types) and ':' in viewspec:
            viewspec, remainder = viewspec.split(':', 1)
            delegated_route = self.routefor(viewspec)

            p1, remainder_args, remainder_kwargs = \
                    delegated_route.path(*args, **kwargs)

            factory_args = args[:-len(remainder_args)]
            factory_kwargs = {k: v for k, v in kwargs.items()
                                   if k not in remainder_kwargs}
            rc = delegated_route.routecollectionfactory(*factory_args,
                                                        **factory_kwargs)
            p2 = rc.pathfor(remainder, *args, **kwargs)
            return p1 + p2

        return self.routefor(viewspec).path(*args, **kwargs)[0]

    def routefor(self, viewspec):
        """
        Return the :class:`~fresco.routing.Route` instance associated with
        ``viewspec``.

        Views may have multiple routes bound, in this case the first bound
        route will always take precedence.

        This method does not resolve delegated routes.

        :param viewspec: a view callable or a string in the form
                         'package.module.viewfunction'
        """

        try:
            return self.__routed_views__[viewspec]
        except KeyError:
            if not isinstance(viewspec, string_types):
                raise RouteNotFound(viewspec)

            modname, symbols = viewspec, []
            while True:
                try:
                    modname, sym = modname.rsplit('.', 1)
                except ValueError:
                    raise RouteNotFound(viewspec)

                symbols.append(sym)
                module = sys.modules.get(modname, None)
                if module:
                    ob = module
                    for s in reversed(symbols):
                        ob = getattr(ob, s)
                    try:
                        route = self.__routed_views__[ob]
                    except KeyError:
                        # An unbound class method? (python 2 only)
                        try:
                            route = self.__routed_views__[ob.__func__]
                        except (AttributeError, KeyError):
                            raise RouteNotFound(viewspec)

                    self.__routed_views__[viewspec] = route
                    return route

    def get_routes(self, path, method):
        """
        Generate routes matching the given path and method::

            for rt in routecollection.get_routes('/foo/bar', GET):
                print("Route is", rt.route)
                print("Arguments extracted from the path:", rt.args, rt.kwargs)
                print("RouteCollections are:", rt.collections_traversed)

        :param request: a :class:`~fresco.request.Request` object
        :param path: the URL path to match (usually this is ``PATH_INFO``)
        :param method: the HTTP method to match (usually this is
                       ``REQUEST_METHOD``). May be ``None``, in which case
                       matching will be performed on the ``path`` argument
                       only.

        :return: A generator yielding ``RouteTraversal`` objects
        """
        for route in self.__routes__:

            result = route.match(path, method)
            if result is None:
                continue

            view_args = result.args
            view_kwargs = {}
            if route.view_kwargs:
                view_kwargs.update(route.view_kwargs)
            view_kwargs.update(result.kwargs)

            if isinstance(route, DelegateRoute):
                try:
                    sub_routes = route.routecollectionfactory(*view_args,
                                                              **view_kwargs)

                except ResponseException as e:
                    def raiser(*args, **kwargs):
                        raise e
                    yield RouteTraversal(Route('/', ALL_METHODS, raiser),
                                         (), {},
                                         [(self, '')])
                    continue
                # Dynamic routes exhaust their arguments when creating the sub
                # RouteCollection.
                if route.dynamic:
                    view_args = ()
                    view_kwargs = {}
                for sub in sub_routes.get_routes(result.path_remaining,
                                                 method):
                    traversed = [(self, '')]
                    traversed.extend((c, result.path_matched + p)
                                     for c, p in sub.collections_traversed)
                    yield RouteTraversal(sub.route,
                                         view_args + sub.args,
                                         dict(view_kwargs, **sub.kwargs),
                                         traversed)
            else:
                yield RouteTraversal(route,
                                     view_args, view_kwargs,
                                     [(self, '')])

    def route(self, pattern, methods, view=None, *args, **kwargs):
        """
        Match a URL pattern to a view function. Can be used as a function
        decorator, in which case the ``view`` parameter should not be passed.

        :param pattern: A string that can be compiled into a path pattern
        :param methods: A list of HTTP methods the view is bound to
        :param view:    The view function. If not specified a function
                        decorator will be returned.

        Other parameters are as for the :class:`Route` constructor.
        """
        # Called as a decorator?
        if view is None:
            def route_decorator(func):
                self.add_route(Route(pattern, methods, func, *args, **kwargs))
                return func
            return route_decorator

        route = Route(pattern, methods, view, *args, **kwargs)
        self.add_route(route)
        return route

    def route_wsgi(self, path, wsgiapp, *args, **kwargs):

        from fresco import context

        def fresco_wsgi_view():
            fake_start_response = lambda status, headers, exc_info=None: None
            return Response.from_wsgi(wsgiapp,
                                      context.request.environ,
                                      fake_start_response)

        return self.route_all(path, ALL_METHODS, fresco_wsgi_view, *args,
                              **kwargs)

    def route_all(self, path, *args, **kwargs):
        """\
        Expose a view for all URLs starting with ``path``.

        :param path: the path prefix at which the view will be routed
        """
        return self.route(MatchAllURLsPattern(path), *args, **kwargs)

    def include(self, path, views):
        """
        Include a view collection at the given path.

        The included view collection's url properties will be modified to
        generate the prefixed URLs.

        :param path:  Path at which to include the views
        :param views: Any collection of views (must expose a ``__routes___``
                      attribute)
        """
        routes = list(r.add_prefix(path) for r in views.__routes__)
        for r in routes:
            r.resolve_view(views)
            self.add_route(r)

    def delegate(self, path, app, dynamic=False, *args, **kwargs):
        """\
        Delegate all requests under ``path`` to ``app``

        :param path: the path prefix at which the app will be available
        :param app: a FrescoApp instance
        """
        route = DelegateRoute(path, app, dynamic, *args, **kwargs)
        self.add_route(route)
        return route


class DelegateRoute(Route):
    """\
    A specialisation of Route that is used to delegate a path prefix to another
    route collection.
    """

    def __init__(self, prefix, view, dynamic=False,
                 *args, **kwargs):
        pattern = ExtensiblePattern(prefix, match_entire_path=False)
        self.dynamic = dynamic
        if self.dynamic:
            self.routecollectionfactory = self._dynamic_routecollectionfactory
        else:
            self.routecollectionfactory = self._static_routecollectionfactory
            if not isinstance(view, RouteCollection):
                view = RouteCollection(view.__routes__)
        super(DelegateRoute, self).__init__(pattern, ALL_METHODS,
                                            view, *args, **kwargs)

    def _dynamic_routecollectionfactory(self, *args, **kwargs):
        """\
        Return the RouteCollection  responsible for paths under this route and
        the remaining positional+keyword args
        """

        cached = context.get(self)
        if cached:
            return cached

        routes = self.view(*args, **kwargs)

        if isinstance(routes, RouteCollection):
            return routes

        for r in routes.__routes__:
            r.resolve_view(routes)

        return RouteCollection(routes.__routes__)

    def _static_routecollectionfactory(self, *args, **kwargs):
        return self.view


class RouteKwarg(object):
    """
    RouteKwarg objects can be used as keyword arguments in a route definition.
    RouteKwargs can extract information from the request and make it available
    to the view.

    For example a RouteKwarg could be developed that reads information from the
    request cookie::

        Route('/', GET, affiliate=CookieArg())

    A naive implementation ``CookieArg`` could look like this::

        class CookieArg(RouteKwarg):

            def __call__(self, request):
                try:
                    return request.cookies[self.name].value
                except KeyError,
                    return None

    When the route is constructed the RouteKwarg's ``configure`` method will
    be called with the Route object and the keyword name.

    At every request, the RouteKwarg instance will be called and expected to
    supply the value for its argument.
    """

    route = None
    name = None

    def configure(self, route, name):
        self.route = route
        self.name = name

    def __call__(self, request):
        return None


class RequestArg(RouteKwarg):
    """
    Extract a view keyword argument from the request object.

    """
    query = attrgetter('query')
    form = attrgetter('form')
    cookies = attrgetter('cookies')
    session = attrgetter('session')

    #: Source for the request variable
    source = form

    #: Exceptions that signal the converter could not do its job due to invalid
    #: input
    converter_exceptions = (ValueError, TypeError)

    _marker = object()

    def __init__(self, converter=None, key=None,
                 default=_marker, exception=BadRequest):

        self.formkey = key
        self.default = default
        self.required = default is self._marker
        self.exception = exception
        self.is_list = isinstance(converter, list)
        if self.is_list:
            self.converter = lambda vs: [c(v)
                                         for c, v in zip(cycle(converter), vs)]
        else:
            self.converter = converter

    def configure(self, route, name):
        if self.formkey is None:
            self.formkey = name
        if self.is_list:
            self.getter = methodcaller('getlist', self.formkey)
        else:
            self.getter = itemgetter(self.formkey)

    def __call__(self, request):
        try:
            value = self.getter(self.source(request))
        except KeyError:
            if self.required:
                raise self.exception('No value provided for %s' %\
                                     (self.formkey,))
            return self.default

        try:
            if self.converter is not None:
                value = self.converter(value)
        except self.converter_exceptions:
            raise self.exception('%r is not a valid value for %s' %\
                                 (value, self.formkey,))

        return value


class CookieArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.cookies``.

    Example::

        @app.route('/', GET, message=CookieArg(key='msg', default=None))
        def view(message):
            return Response([message])
    """
    source = RequestArg.cookies

    def getter(self, cookies):
        if self.is_list:
            return [c.value for c in cookies.getlist(self.formkey)]
        else:
            return cookies[self.formkey].value

    def configure(self, route, name):
        if self.formkey is None:
            self.formkey = name


class QueryArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.query``.

    Example::

        @app.route('/add', GET, a=QueryArg(int), b=QueryArg(int))
        def view(a, b):
            return Response(['a + b = %d' % (a + b)])
    """
    source = RequestArg.query


class FormArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.form``.

    Example::

        @app.route('/mul', POST, a=FormArg(int), b=FormArg(int))
        def view(a, b):
            return Response(['a * b = %d' % (a * b)])

    """
    source = RequestArg.form


class SessionArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.form``.

    Example::

        @app.route('/mul', POST, a=FormArg(int), b=FormArg(int))
        def view(a, b):
            return Response(['a * b = %d' % (a * b)])

    """
    source = RequestArg.session


class From(object):
    """\
    Accessors for RequestArg classes::

        from fresco.routing import Route, From

        Route('/blah', GET, x=From.get(), y=From.cookie())

    """
    form = FormArg
    query = QueryArg
    get = QueryArg
    post = FormArg
    cookie = CookieArg
    session = SessionArg
