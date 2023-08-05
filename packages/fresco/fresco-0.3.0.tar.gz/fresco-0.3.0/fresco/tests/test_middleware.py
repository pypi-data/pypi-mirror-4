from fresco import FrescoApp, context, GET, Response
from fresco.middleware import XForwarded
from flea import TestAgent


class TestXForwarded(object):

    def get_app(self, *args, **kwargs):
        app = FrescoApp()

        @app.route('/', GET)
        def view():
            request = context.request
            return Response([request.url, ' ', request.environ['REMOTE_ADDR']])
        return XForwarded(app, *args, **kwargs)

    def test_forwards_x_forwarded_for(self):

        r = TestAgent(self.get_app())
        r = r.get('/', REMOTE_ADDR='127.0.0.1', HTTP_X_FORWARDED_FOR='1.2.3.4')
        url, addr = r.body.split(' ')
        assert addr == '1.2.3.4'

    def test_forwards_x_forwarded_host(self):

        r = TestAgent(self.get_app())
        r = r.get('/', REMOTE_ADDR='127.0.0.1',
                  HTTP_X_FORWARDED_HOST='frontendserver')
        url, addr = r.body.split(' ')
        assert url == 'http://frontendserver/'

    def test_forwards_x_forwarded_ssl(self):

        r = TestAgent(self.get_app())
        r = r.get('/', REMOTE_ADDR='127.0.0.1',
                  HTTP_X_FORWARDED_SSL='on',
                  HTTP_X_FORWARDED_HOST='localhost')
        url, addr = r.body.split(' ')
        assert url == 'https://localhost/', url

        r = TestAgent(self.get_app())
        r = r.get('/', REMOTE_ADDR='127.0.0.1',
                  HTTP_X_FORWARDED_SSL='off',
                  HTTP_X_FORWARDED_HOST='localhost')
        url, addr = r.body.split(' ')
        assert url == 'http://localhost/'

    def test_reports_first_trusted_ip(self):
        r = TestAgent(self.get_app(trusted=['127.0.0.1', '3.3.3.3']))
        r = r.get('/', REMOTE_ADDR='127.0.0.1',
                  HTTP_X_FORWARDED_FOR='1.1.1.1, 2.2.2.2, 3.3.3.3')
        url, addr = r.body.split(' ')
        assert addr == '2.2.2.2'

    def test_reports_first_listed_ip_as_remote_addr_when_untrusted(self):
        r = TestAgent(self.get_app())
        r = r.get('/', REMOTE_ADDR='127.0.0.1',
                  HTTP_X_FORWARDED_FOR='1.1.1.1, 2.2.2.2')
        url, addr = r.body.split(' ')
        assert addr == '1.1.1.1'
