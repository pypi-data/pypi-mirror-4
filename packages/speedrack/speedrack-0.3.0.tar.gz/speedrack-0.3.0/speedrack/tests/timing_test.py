
from nose.tools import *

from speedrack import timing

class TestTiming(object):

    def check_interval_parse(self, test, expected):
        assert_equal(expected, timing.parse_interval(test))

    def test_interval_parse(self):
        tests = [
            ("3h", {"hours": 3} ),
            ("2m", {"minutes": 2} ),
            ("20s", {"seconds": 20} ),
            ("4M", {"months": 4} ),
            ("5w", {"weeks": 5} ),
            ({}, None),
        ]
        for (test, expected) in tests:
            yield self.check_interval_parse, test, expected

    def check_cron_parse(self, test, expected):
        assert_equal(expected, timing.parse_cron(test))

    def test_cron_parse(self):
        tests = [
            ({ 'second': 15, 'minutes': 30 }, False),
            ({ 'second': 15, 'minute': 15 }, { 'second': 15, 'minute': 15 }),
            ({}, None),
        ]
        for (test, expected) in tests:
            yield self.check_cron_parse, test, expected
