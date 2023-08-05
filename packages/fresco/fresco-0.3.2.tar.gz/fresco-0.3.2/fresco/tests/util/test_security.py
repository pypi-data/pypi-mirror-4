from nose.tools import assert_equal, assert_raises

from fresco.util import security

class TestSecurity(object):

    def test_check_equal_constant_time_returns_equality(self):
        assert_equal(security.check_equal_constant_time('', ''), True)
        assert_equal(security.check_equal_constant_time('abcabcabc', 'abcabcabc'), True)

    def test_check_equal_constant_time_returns_inequality(self):
        assert_equal(security.check_equal_constant_time(' ', ''), False)
        assert_equal(security.check_equal_constant_time('abcabcabc', 'abcabcabx'), False)
        assert_equal(security.check_equal_constant_time('abcabcabc', 'abcabcabx'), False)
        assert_equal(security.check_equal_constant_time('abcabcabc', 'abcabcabde'), False)
        assert_equal(security.check_equal_constant_time('abcabcabc', 'abcabcab'), False)

    def test_check_equal_constant_time_raises_an_error_on_non_strings(self):
        assert_raises(TypeError, security.check_equal_constant_time, (None, None))
