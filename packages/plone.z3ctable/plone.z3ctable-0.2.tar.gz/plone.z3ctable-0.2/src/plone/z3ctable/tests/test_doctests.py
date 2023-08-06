from unittest import TestSuite
from zope.testing import doctest
from Testing import ZopeTestCase as ztc

from z3c.table.testing import setUp
from z3c.table.testing import tearDown

optionflags = (
               doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return TestSuite([
        ztc.FunctionalDocFileSuite(
           'provider.txt', package='plone.z3ctable.tests',
           setUp=setUp, tearDown=tearDown, optionflags=optionflags),
        ])
