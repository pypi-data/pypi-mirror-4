# -*- coding: utf-8 -*-

import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from tlspu.cookiepolicy.testing import INTEGRATION_TESTING


class PortalSetupTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_uninstall_profile(self):
        # Applying the uninstall profile should not give errors.
        setup_tool = getToolByName(self.portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile(
            'profile-tlspu.cookiepolicy:uninstall')


class UninstallTest(unittest.TestCase):
    """Test if uninstall works well.
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = getToolByName(self.portal, 'portal_quickinstaller')
        # Uninstall via portal_quickinstaller should not give errors.
        self.qi.uninstallProducts(products=['tlspu.cookiepolicy'])

    def test_configlet_removed(self):
        controlpanel = getToolByName(self.portal, 'portal_controlpanel')
        installed = [a.getAction(self)['id']
                     for a in controlpanel.listActions()]
        self.assertFalse('cookiepolicy' in installed)

    def test_properties_removed(self):
        pp = getToolByName(self.portal, 'portal_properties')
        self.assertFalse(hasattr(pp, 'tlspu_cookiepolicy_properties'))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
