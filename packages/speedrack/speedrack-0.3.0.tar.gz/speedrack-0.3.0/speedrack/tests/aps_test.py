from nose.tools import *

from speedrack import aps

class TestAps(object):

    def check_understate(self, test, expected):
        assert_equal(expected, aps.understate(test))

    def test_understate(self):
        tests = [
            ("basic", "basic"),
            ("add this name", "add_this_name"),
            ("!@$%#&", ""),
            ("underscore ALL THE THINGS!", "underscore_all_the_things"),
            # note that ' (' becomes single _
            ("useless (parenthetical)", "useless_parenthetical"),
        ]
        for (test, expected) in tests:
            yield self.check_understate, test, expected
