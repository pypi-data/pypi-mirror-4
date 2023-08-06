from datetime import timedelta
import unittest2 as unittest

from mtj.f3u1.units import Time


class TimeUnitTestCase(unittest.TestCase):
    """
    Unit tests for the original hour-based requirements.
    """

    def test_zeros(self):
        self.assertEqual(Time.units['second'](0), [('second', 0)])
        self.assertEqual(Time.units['second'](0), [('second', 0)])
        self.assertEqual(Time.units['minute'](0), [('minute', 0)])
        self.assertEqual(Time.units['minute'](0), [('minute', 0)])
        self.assertEqual(Time.units['hour'](0), [('hour', 0)])
        self.assertEqual(Time.units['hour'](0), [('hour', 0)])
        self.assertEqual(Time.units['day'](0), [('day', 0)])
        self.assertEqual(Time.units['day'](0), [('day', 0)])
        # Duplicates abound but whatever.

    def test_singular(self):
        self.assertEqual(Time.units['second'](1), [('second', 1)])
        self.assertEqual(Time.units['second'](1), [('second', 1)])

    def test_plural(self):
        self.assertEqual(Time.units['second'](2), [('second', 2)])

    def test_almost_next(self):
        self.assertEqual(Time.units['second'](59), [('second', 59)])
        self.assertEqual(Time.units['minute'](59), [('minute', 0)])

    def test_minute(self):
        self.assertEqual(Time.units['second'](60), [('minute', 1)])
        self.assertEqual(Time.units['minute'](60), [('minute', 1)])

    def test_minute_plusone(self):
        self.assertEqual(Time.units['second'](61),
            [('minute', 1), ('second', 1)])
        self.assertEqual(Time.units['minute'](61), [('minute', 1)])

    def test_day_minusone(self):
        self.assertEqual(Time.units['second'](86399),
            [('hour', 23), ('minute', 59), ('second', 59)])
        self.assertEqual(Time.units['minute'](86399),
            [('hour', 23), ('minute', 59)])
        self.assertEqual(Time.units['hour'](86399), [('hour', 23)])
        self.assertEqual(Time.units['day'](86399), [('day', 0)])

    def test_day(self):
        self.assertEqual(Time.units['second'](86400), [('day', 1)])
        self.assertEqual(Time.units['minute'](86400), [('day', 1)])
        self.assertEqual(Time.units['hour'](86400), [('day', 1)])
        self.assertEqual(Time.units['day'](86400), [('day', 1)])

    def test_day_pluseone(self):
        self.assertEqual(Time.units['second'](86401),
            [('day', 1), ('second', 1)])
        self.assertEqual(Time.units['minute'](86401), [('day', 1)])
        self.assertEqual(Time.units['hour'](86401), [('day', 1)])
        self.assertEqual(Time.units['day'](86401), [('day', 1)])

    def test_day_pluseoneminute(self):
        self.assertEqual(Time.units['second'](86460),
            [('day', 1), ('minute', 1)])
        self.assertEqual(Time.units['minute'](86460),
            [('day', 1), ('minute', 1)])
        self.assertEqual(Time.units['hour'](86460), [('day', 1)])
        self.assertEqual(Time.units['day'](86460), [('day', 1)])

    def test_day_pluseonehour(self):
        self.assertEqual(Time.units['second'](90000),
            [('day', 1), ('hour', 1)])
        self.assertEqual(Time.units['minute'](90000),
            [('day', 1), ('hour', 1)])
        self.assertEqual(Time.units['hour'](90000),
            [('day', 1), ('hour', 1)])
        self.assertEqual(Time.units['day'](90000),
            [('day', 1)])

    def test_more(self):
        self.assertEqual(Time.units['second'](901101),
            [('day', 10), ('hour', 10), ('minute', 18), ('second', 21)])
        self.assertEqual(Time.units['minute'](901101),
            [('day', 10), ('hour', 10), ('minute', 18)])
        self.assertEqual(Time.units['hour'](901101),
            [('day', 10), ('hour', 10)])
        self.assertEqual(Time.units['day'](901101), [('day', 10)])


class TimeConstructionTestCase(unittest.TestCase):
    """
    Unit tests for having a constructed Time unit.

    This essentially tests the implementation of the encapsulated
    UnitValue class.
    """

    def test_basic(self):
        self.assertEqual(str(Time()), '0 seconds')
        self.assertEqual(str(Time(second=1)), '1 second')
        self.assertEqual(str(Time(second=2)), '2 seconds')
        self.assertEqual(str(Time(minute=0)), '0 seconds')
        self.assertEqual(str(Time(minute=1)), '1 minute')
        self.assertEqual(str(Time(minute=2)), '2 minutes')
        self.assertEqual(str(Time(minute=2, second=2)), '2 minutes, 2 seconds')
        self.assertEqual(str(Time(second=122)), '2 minutes, 2 seconds')
        self.assertEqual(str(Time(day=2, second=2)), '2 days, 2 seconds')
        self.assertEqual(str(Time(second=262803)), '3 days, 1 hour, 3 seconds')

    def test_resolution(self):
        self.assertEqual(str(Time('hour')), '0 hours')
        self.assertEqual(str(Time('hour', second=1)), '0 hours')
        self.assertEqual(str(Time('hour', second=2)), '0 hours')
        self.assertEqual(str(Time('hour', minute=0)), '0 hours')
        self.assertEqual(str(Time('hour', minute=1)), '0 hours')
        self.assertEqual(str(Time('hour', minute=2)), '0 hours')
        self.assertEqual(str(Time('hour', day=2, second=2)), '2 days')
        self.assertEqual(str(Time('hour', second=262803)), '3 days, 1 hour')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TimeUnitTestCase))
    suite.addTest(unittest.makeSuite(TimeConstructionTestCase))
    return suite
