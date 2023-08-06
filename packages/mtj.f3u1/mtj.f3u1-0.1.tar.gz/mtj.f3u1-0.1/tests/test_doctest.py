import unittest2 as unittest
import doctest

def test_suite():
    return unittest.TestSuite([

        # Base
        doctest.DocFileSuite(
            'README.rst', package='mtj.f3u1',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
