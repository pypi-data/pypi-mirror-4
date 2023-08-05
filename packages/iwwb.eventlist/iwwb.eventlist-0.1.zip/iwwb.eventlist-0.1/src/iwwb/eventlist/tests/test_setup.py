# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from iwwb.eventlist.tests.base import IntegrationTestCase
from Products.CMFCore.utils import getToolByName

import unittest2 as unittest


class TestSetup(IntegrationTestCase):
    """Test installation of iwwb.eventlist into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_installed(self):
        """Test if iwwb.eventlist is installed with portal_quickinstaller."""
        self.failUnless(self.installer.isProductInstalled('iwwb.eventlist'))

    def test_uninstall(self):
        """Test if iwwb.eventlist is cleanly uninstalled."""
        self.installer.uninstallProducts(['iwwb.eventlist'])
        self.failIf(self.installer.isProductInstalled('iwwb.eventlist'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IIWWBEventlistLayer is registered."""
        from iwwb.eventlist.interfaces import IIWWBEventlistLayer
        from plone.browserlayer import utils
        self.failUnless(IIWWBEventlistLayer in utils.registered_layers())


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
