""" Doc tests
"""
import unittest
import doctest
from plone.testing import layered
from edw.userhistory.tests import base

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Suite
    """
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(
                    'docs/portlet.txt',
                    package='edw.userhistory',
                    optionflags=OPTIONFLAGS),
                layer=base.FUNCTIONAL_TESTING),
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
