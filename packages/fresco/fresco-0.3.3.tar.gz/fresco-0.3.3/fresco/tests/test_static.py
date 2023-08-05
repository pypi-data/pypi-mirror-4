import os
import re
from calendar import timegm
from email.utils import formatdate, parsedate
from mock import Mock
from tempfile import mkstemp
from fresco import FrescoApp
from fresco.static import serve_static_file


class TestServeStaticFile():

    def setup(self):

        fh, tmpname = mkstemp()
        self.tmpname = tmpname
        self.mtime = int(os.path.getmtime(self.tmpname))
        os.close(fh)

    def teardown(self):
        os.unlink(self.tmpname)

    def parse_lmh(self, last_modified):
        return timegm(parsedate(last_modified))

    def make_ims(self, since, tz=0):
        return {'HTTP_IF_MODIFIED_SINCE': formatdate(since, tz)}

    def test_sets_last_modified_header(self):
        with FrescoApp().requestcontext():
            response = serve_static_file(self.tmpname)
            response.content.close()

        last_modified = response.get_header('Last-Modified')
        assert self.parse_lmh(last_modified) == self.mtime

    def test_full_response_when_if_modified_before_mtime(self):
        with FrescoApp().requestcontext(**self.make_ims(0)):
            response = serve_static_file(self.tmpname)
            response.content.close()

        last_modified = response.get_header('Last-Modified')
        assert response.status_code == 200
        assert self.parse_lmh(last_modified) == self.mtime

    def test_304_when_if_modified_after_mtime(self):
        with FrescoApp().requestcontext(**self.make_ims(self.mtime + 1)):
            response = serve_static_file(self.tmpname)
        assert response.status_code == 304

    def test_304_when_if_modified_after_mtime_with_tz1(self):
        with FrescoApp().requestcontext(**self.make_ims(self.mtime + 1, +1)):
            response = serve_static_file(self.tmpname)
        assert response.status_code == 304

    def test_304_when_if_modified_after_mtime_with_tz2(self):
        with FrescoApp().requestcontext(**self.make_ims(self.mtime + 1, -1)):
            response = serve_static_file(self.tmpname)
        assert response.status_code == 304

    def test_last_modified_format_is_correct(self):
        with FrescoApp().requestcontext():
            response = serve_static_file(self.tmpname)
            response.content.close()

        assert re.match(r'^\w{3}, \d{1,2} \w{3} \d{4} \d\d:\d\d:\d\d GMT',
                        response.get_header('last-modified'))

    def test_filewrapper_used_if_present(self):
        with FrescoApp().requestcontext() as c:
            file_wrapper = Mock(return_value=[])
            c.request.environ['wsgi.file_wrapper'] = file_wrapper
            serve_static_file(self.tmpname)

        file_wrapper.assert_called_once()
