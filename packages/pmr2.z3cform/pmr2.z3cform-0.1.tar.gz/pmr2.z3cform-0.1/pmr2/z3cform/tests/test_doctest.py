import unittest
import doctest

from Testing import ZopeTestCase as ztc

from pmr2.z3cform.tests import base


def test_suite():
    return unittest.TestSuite([

        # Doctest for PMR2 pages
        ztc.ZopeDocFileSuite(
            'page.rst', package='pmr2.z3cform',
            test_class=base.DocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Doctest for PMR2 forms
        ztc.ZopeDocFileSuite(
            'form.rst', package='pmr2.z3cform',
            test_class=base.DocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
