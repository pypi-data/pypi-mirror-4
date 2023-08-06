import gocept.autocomplete.testing
import unittest
import zope.testing.doctest


optionflags = (zope.testing.doctest.REPORT_NDIFF
               | zope.testing.doctest.NORMALIZE_WHITESPACE
               | zope.testing.doctest.ELLIPSIS)


def test_suite():
    suite = zope.testing.doctest.DocFileSuite('README.txt',
                                              package='gocept.autocomplete',
                                              optionflags=optionflags)
    suite.layer = gocept.autocomplete.testing.functional_layer
    return unittest.TestSuite()  # skip test for now
