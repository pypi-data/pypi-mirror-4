import unittest
import doctest

from Testing import ZopeTestCase as ztc

from pmr2.captcha.tests import base


def test_suite():
    return unittest.TestSuite([

        # Doctest for the customized registration form
        ztc.ZopeDocFileSuite(
            'register.txt', package='pmr2.captcha.browser',
            test_class=base.TestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
