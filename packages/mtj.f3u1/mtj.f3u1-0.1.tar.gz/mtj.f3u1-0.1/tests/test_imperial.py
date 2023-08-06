from datetime import timedelta
import unittest2 as unittest

from mtj.f3u1.units import ImperialLength, ImperialWeight


class ImperialUnitsTestCase(unittest.TestCase):
    """
    Imperial units.
    """

    def test_length(self):
        self.assertEqual(ImperialLength.units['inch'](14),
            [('foot', 1), ('inch', 2)])
        self.assertEqual(ImperialLength.units['inch'](25),
            [('foot', 2), ('inch', 1)])
        self.assertEqual(ImperialLength.units['inch'](63390),
            [('mile', 1), ('foot', 2), ('inch', 6)])

    def test_weight(self):
        self.assertEqual(ImperialWeight.units['ounce'](223),
            [('pound', 13), ('ounce', 15)])
        self.assertEqual(ImperialWeight.units['ounce'](225),
            [('stone', 1), ('ounce', 1)])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ImperialUnitsTestCase))
    return suite
