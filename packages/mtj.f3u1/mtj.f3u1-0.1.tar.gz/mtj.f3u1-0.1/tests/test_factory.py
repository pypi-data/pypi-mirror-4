from datetime import timedelta
import unittest2 as unittest

from mtj.f3u1.factory import units_factory, unit_number_tuple_to_str
from mtj.f3u1.factory import UnitGroup


class FactoryTestCase(unittest.TestCase):
    """
    Unit tests for the units_factory function.
    """

    def test_factory_construct_fail(self):
        self.assertRaises(AssertionError, units_factory, 'fail', 1, object())

    def test_factory_normal(self):
        unit = units_factory('unit', 1)
        self.assertEqual(unit(0), [('unit', 0)])
        unit = units_factory('unit', 1)
        self.assertEqual(unit(0), [('unit', 0)])
        self.assertEqual(unit(1), [('unit', 1)])

    def test_factory_chained(self):
        ten = units_factory('ten', 10)
        unit = units_factory('unit', 1, higher_unit=ten)
        self.assertEqual(unit(0), [('unit', 0)])
        self.assertEqual(unit(9), [('unit', 9)])
        self.assertEqual(ten(9), [('ten', 0)])
        self.assertEqual(unit(10), [('ten', 1)])
        self.assertEqual(ten(10), [('ten', 1)])
        self.assertEqual(unit(11), [('ten', 1), ('unit', 1)])
        self.assertEqual(unit(20), [('ten', 2)])

    def test_factory_base_omissible(self):
        # this really means blank value on empty.
        unit = units_factory('unit', 1, omissible=True)
        self.assertEqual(unit(0), [])
        self.assertEqual(unit(1), [('unit', 1)])
        ten = units_factory('ten', 10, omissible=True)
        unit = units_factory('unit', 1, higher_unit=ten, omissible=True)
        self.assertEqual(ten(9), [])
        self.assertEqual(ten(10), [('ten', 1)])

    def test_factory_higher_omissible(self):
        unit = units_factory('unit', 1, force_render=True)
        self.assertEqual(unit(0), [('unit', 0)])
        self.assertEqual(unit(1), [('unit', 1)])
        hundred = units_factory('hundred', 100, force_render=True)
        ten = units_factory('ten', 10, higher_unit=hundred,
            force_render=True)
        unit = units_factory('unit', 1, higher_unit=ten,
            force_render=True)

        self.assertEqual(ten(9), [('hundred', 0), ('ten', 0)])
        self.assertEqual(unit(0), [('hundred', 0), ('ten', 0), ('unit', 0)])
        self.assertEqual(unit(9), [('hundred', 0), ('ten', 0), ('unit', 9)])

        self.assertEqual(unit(10), [('hundred', 0), ('ten', 1), ('unit', 0)])
        self.assertEqual(ten(10), [('hundred', 0), ('ten', 1)])

    def test_factory_higher_irregular(self):
        gross = units_factory('gross', 144)
        hundred = units_factory('hundred', 100, higher_unit=gross)
        dozen = units_factory('dozen', 12, higher_unit=hundred)
        ten = units_factory('ten', 10, higher_unit=dozen)
        unit = units_factory('unit', 1, higher_unit=ten)

        self.assertEqual(unit(9), [('unit', 9)])
        self.assertEqual(unit(10), [('ten', 1)])
        self.assertEqual(unit(12), [('dozen', 1)])
        self.assertEqual(unit(23), [('dozen', 1), ('ten', 1), ('unit', 1)])
        self.assertEqual(unit(24), [('dozen', 2)])
        self.assertEqual(unit(26), [('dozen', 2), ('unit', 2)])
        self.assertEqual(unit(99), [('dozen', 8), ('unit', 3)])
        self.assertEqual(unit(100), [('hundred', 1)])
        self.assertEqual(unit(111), [('hundred', 1), ('ten', 1), ('unit', 1)])
        self.assertEqual(unit(112), [('hundred', 1), ('dozen', 1)])
        self.assertEqual(unit(143), [('hundred', 1), ('dozen', 3), ('unit', 7)])
        self.assertEqual(unit(144), [('gross', 1)])
        self.assertEqual(unit(150), [('gross', 1), ('unit', 6)])
        self.assertEqual(unit(155), [('gross', 1), ('ten', 1), ('unit', 1)])
        self.assertEqual(unit(156), [('gross', 1), ('dozen', 1)])
        self.assertEqual(unit(287),
            [('gross', 1), ('hundred', 1), ('dozen', 3), ('unit', 7)])
        self.assertEqual(unit(288), [('gross', 2)])


class UnitGroupTestCase(unittest.TestCase):
    """
    Unit tests for the UnitGroup class.
    """

    def setUp(self):
        self.time_ratios = {
            'week': 604800,
            'day': 86400,
            'hour': 3600,
            'minute': 60,
        }

    def test_construction(self):
        timeug = UnitGroup(base_unit='second', ratios=self.time_ratios)
        self.assertEqual(timeug.units['hour'](86461), [('day', 1)])
        self.assertEqual(timeug.units['hour'](90061), [('day', 1), ('hour', 1)])
        self.assertEqual(timeug.units['week'](90061), [('week', 0)])
        self.assertEqual(timeug.units['second'](1940464),
            [('week', 3), ('day', 1), ('hour', 11), ('minute', 1), ('second', 4)])

    def test_construction_baseunit_redefinition_omitted(self):
        ug = UnitGroup(base_unit='second', ratios={
            'hour': 3600, 'second': 60,})
        self.assertEqual(ug.units['second'](71), [('second', 71)])

        # To show the difference
        ug = UnitGroup(base_unit='nope', ratios={
            'hour': 3600, 'second': 60,})
        self.assertEqual(ug.units['nope'](71), [('second', 1), ('nope', 11)])

    def test_respecify_new_ratio(self):
        timeug = UnitGroup(base_unit='second', ratios=self.time_ratios)
        # original
        self.assertEqual(timeug.units['second'](9954862),
            [('week', 16), ('day', 3), ('hour', 5), ('minute', 14), ('second', 22)])
        self.assertEqual(timeug.units['second'](2592000),
            [('week', 4), ('day', 2)])
        self.assertEqual(timeug.units['second'](3196800),
            [('week', 5), ('day', 2)])
        self.assertEqual(timeug.units['second'](7775940),
            [('week', 12), ('day', 5), ('hour', 23), ('minute', 59)])

        monthug = timeug.respecify({'month': 2592000})
        self.assertEqual(monthug.units['second'](2592000),
            [('month', 1)])
        self.assertEqual(monthug.units['second'](3196800),
            [('month', 1), ('week', 1)])
        self.assertEqual(monthug.units['second'](7775940),
            [('month', 2), ('week', 4), ('day', 1), ('hour', 23), ('minute', 59)])

    def test_respecify_new_ratio_keep(self):
        timeug = UnitGroup(base_unit='second', ratios=self.time_ratios)
        # can't filter base units out.
        monthug = timeug.respecify({'month': 2592000}, keep_only=['month'])
        self.assertEqual(monthug.units['second'](2592000),
            [('month', 1)])
        self.assertEqual(monthug.units['second'](3196800),
            [('month', 1), ('second', 604800)])

    def test_respecify_drop(self):
        timeug = UnitGroup(base_unit='second', ratios=self.time_ratios)
        # can't drop base units.
        monthug = timeug.respecify({'month': 2592000}, drop=['week', 'second'])
        self.assertEqual(sorted(monthug.ratios.keys()),
            ['day', 'hour', 'minute', 'month', 'second'])
        self.assertEqual(monthug.units['second'](2592000),
            [('month', 1)])
        self.assertEqual(monthug.units['second'](3196801),
            [('month', 1), ('day', 7), ('second', 1)])

    def test_respecify_new_ratio_and_drop(self):
        timeug = UnitGroup(base_unit='second', ratios=self.time_ratios)
        # can't filter base units out.
        monthug = timeug.respecify({'month': 2592000}, keep_only=['month'],
            drop=['month'])
        self.assertEqual(sorted(monthug.ratios.keys()), ['second'])
        self.assertEqual(monthug.units['second'](2592000),
            [('second', 2592000)])


class FormatUnitNumbers(unittest.TestCase):

    def test_format(self):
        self.assertEqual('1 unit',
            unit_number_tuple_to_str([('unit', 1)], {'unit': 'units'}))
        self.assertEqual('2 units',
            unit_number_tuple_to_str([('unit', 2)], {'unit': 'units'}))
        self.assertEqual('3 unit',
            unit_number_tuple_to_str([('unit', 3)], None))
        self.assertEqual('1 ten, 1 unit',
            unit_number_tuple_to_str([('ten', 1), ('unit', 1)],
                {'unit': 'units', 'ten': 'tens'}))
        self.assertEqual('2 ten, 2 units',
            unit_number_tuple_to_str([('ten', 2), ('unit', 2)],
                {'unit': 'units'}))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FactoryTestCase))
    suite.addTest(unittest.makeSuite(FormatUnitNumbers))
    suite.addTest(unittest.makeSuite(UnitGroupTestCase))
    return suite
