
import unittest

from slimta.logging import logline, parseline


class TestLogging(unittest.TestCase):

    def _check_logline(self, expected):
        def check(data):
            self.assertEqual(expected, data)
        return check

    def test_logline_nodata(self):
        check = self._check_logline('test:asdf:nodata')
        logline(check, 'test', 'asdf', 'nodata')

    def test_logline_withdata(self):
        check = self._check_logline('test:asdf:withdata one=1 two=\'two\'')
        logline(check, 'test', 'asdf', 'withdata', one=1, two='two')

    def test_parseline_nodata(self):
        line = 'test:jkl:nodata'
        type, id, op, data = parseline(line)
        self.assertEqual('test', type)
        self.assertEqual('jkl', id)
        self.assertEqual('nodata', op)
        self.assertEqual({}, data)

    def test_parseline_withdata(self):
        line = 'test:jkl:withdata one=1 two=\'two\''
        type, id, op, data = parseline(line)
        self.assertEqual('test', type)
        self.assertEqual('jkl', id)
        self.assertEqual('withdata', op)
        self.assertEqual({'one': 1, 'two': 'two'}, data)

    def test_parseline_badbeginning(self):
        with self.assertRaises(ValueError):
            parseline('bad!')

    def test_parseline_baddata(self):
        line = 'test:jkl:baddata one=1 two=two'
        type, id, op, data = parseline(line)
        self.assertEqual('test', type)
        self.assertEqual('jkl', id)
        self.assertEqual('baddata', op)
        self.assertEqual({'one': 1}, data)
        line = 'test:jkl:baddata one=one two=\'two\''
        type, id, op, data = parseline(line)
        self.assertEqual('test', type)
        self.assertEqual('jkl', id)
        self.assertEqual('baddata', op)
        self.assertEqual({}, data)


# vim:et:fdm=marker:sts=4:sw=4:ts=4
