import unittest
from base import ZETTWERK_UI_INTEGRATION_TESTING

from Products.CMFCore.utils import getToolByName


class TestInstallation(unittest.TestCase):

    layer = ZETTWERK_UI_INTEGRATION_TESTING

    def test_tool_installed(self):
        portal = self.layer['portal']
        quickinstaller = getToolByName(portal,
                                       'portal_quickinstaller')
        self.assertTrue(quickinstaller.isProductInstalled('zettwerk.ui'))

        ## also check the tool object
        self.failUnless(getattr(portal, 'portal_ui_tool', None))

    def test_tool_uninstall(self):
        portal = self.layer['portal']
        quickinstaller = getToolByName(portal,
                                       'portal_quickinstaller')
        quickinstaller.uninstallProducts(['zettwerk.ui'])

        self.assertFalse(quickinstaller.isProductInstalled('zettwerk.ui'))

        ## also check the tool object
        self.assertTrue(getattr(portal, 'portal_ui_tool', None) is None)

        ## check if uninstaller profile has removed the control panel action
        self.assertTrue(
            'zettwerkui' not in \
                [a.getId() for a in portal.portal_controlpanel.listActions()]
            )
