# -*- coding: utf-8 -*-

import unittest
import doctest

from plone.testing import layered

from collective.portaltabs.testing import PORTAL_TABS_FUNCTIONAL_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
                    layered(doctest.DocFileSuite('simple.txt'), layer=PORTAL_TABS_FUNCTIONAL_TESTING),
                    layered(doctest.DocFileSuite('edit.txt'), layer=PORTAL_TABS_FUNCTIONAL_TESTING),
                    layered(doctest.DocFileSuite('add.txt'), layer=PORTAL_TABS_FUNCTIONAL_TESTING),
                    layered(doctest.DocFileSuite('multiple_edit.txt'), layer=PORTAL_TABS_FUNCTIONAL_TESTING),
                    layered(doctest.DocFileSuite('moving.txt'), layer=PORTAL_TABS_FUNCTIONAL_TESTING), 
                    ])
    return suite
