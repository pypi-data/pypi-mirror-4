from nose.tools import *

from speedrack import filer

class TestFiler(object):

    def test_get_size_bad(self):
        assert_equals(-1, filer.get_size("non-existant"))

    def test_get_size_good(self):
        assert_true(filer.get_size(__file__) > 0)

    def test_get_humanized_size_bad(self):
        assert_equals(None, filer.get_humanized_size("non-existant"))

    def test_get_humanized_size_good(self):
        assert_true(len(filer.get_humanized_size(__file__)) > 0)

    def test_get_file_summary(self):
        assert_in("... of", filer.get_file_summary(__file__, 10, True))
        assert_not_in("... of", filer.get_file_summary(__file__, 10, False))
        # my trickery ends here
        #assert_not_in("... of", filer.get_file_summary(__file__, max_size=None, append_total=True))

    def check_humanize_sizeof(self, test, expected):
        assert_equals(expected, filer.humanize_sizeof(test))

    def test_humanize_sizeof(self):
        tests = [
            (1000, "1000.0 bytes"),
            (1024, "1.0 KB"),
            (10000, "9.8 KB"),
            (1024 * 1024 - 1, "1024.0 KB"), # doesn't round up
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 + 1, "1.0 MB"),
        ]
        for (test, expected) in tests:
            yield self.check_humanize_sizeof, test, expected
