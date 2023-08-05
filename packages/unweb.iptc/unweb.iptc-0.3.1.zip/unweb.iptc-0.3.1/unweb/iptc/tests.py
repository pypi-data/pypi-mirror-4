# -*- coding: utf-8 -*-
"""Functional Doctests for unweb.iptc

   These test are only triggered when Plone 4 (and plone.testing) is installed.
"""
import doctest

try:
    import unittest2 as unittest
except:
    import unittest

import pprint
import interlude
    
from plone.testing import layered
    
from unweb.iptc.testing import UNWEB_IPTC_FUNCTIONAL_TESTING

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)
normal_testfiles = [
    'browser.txt',
]

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(test ,
                                     optionflags=optionflags,
                                     globs={'interact': interlude.interact,
                                            'pprint': pprint.pprint,
                                            }
                                     ),
                layer=UNWEB_IPTC_FUNCTIONAL_TESTING)
        for test in normal_testfiles])
    return suite

