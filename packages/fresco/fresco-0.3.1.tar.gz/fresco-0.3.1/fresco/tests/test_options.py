import sys
from tempfile import NamedTemporaryFile
from fresco.options import Options


class TestOptions(object):

    def test_options_dictionary_access(self):
        options = Options()
        options['x'] = 1
        assert options['x'] == 1

    def test_options_attribute_access(self):
        options = Options()
        options.x = 1
        assert options.x == 1

    def test_options_update_from_object(self):

        class Foo:
            a = 1
            b = 2

        options = Options()
        options.update_from_object(Foo())
        assert options == {'a': 1, 'b': 2}

    def test_options_update_from_object_loads_underscore_names(self):

        class Foo:
            pass

        options = Options()
        options.update_from_object(Foo(), True)
        assert '__module__' in options

    def test_options_update_from_file(self):

        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b"a = 1\nb = 2\n")
            tmpfile.flush()

            options = Options()
            options.update_from_file(tmpfile.name)
            assert options == {'a': 1, 'b': 2}

    def test_options_respects_all(self):
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b"__all__ = ['a']\n"
                          b"a = 1\n"
                          b"b = 2\n")
            tmpfile.flush()

            options = Options()
            options.update_from_file(tmpfile.name)
            assert options == {'a': 1}

    def test_update_from_file_doesnt_add_module(self):
        with NamedTemporaryFile() as tmpfile:
            options = Options()
            saved_modules = list(sorted(sys.modules.keys()))
            options.update_from_file(tmpfile.name)
            assert list(sorted(sys.modules.keys())) == saved_modules
