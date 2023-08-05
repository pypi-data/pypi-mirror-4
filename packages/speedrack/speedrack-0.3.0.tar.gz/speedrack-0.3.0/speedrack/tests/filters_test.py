from nose.tools import *

from speedrack import filters

class TestFilters(object):
    def setup(self):
        pass

    def test_leading(self):
        assert_equals(filters.leading([1,2,3,4], 2), [1,2])
