import unittest
from base import ZETTWERK_UI_THEMES_INTEGRATION_TESTING
from plone.testing.z2 import Browser
from urllib2 import HTTPError

from zettwerk.ui.resources import registerResourceDirectory


class TestResources(unittest.TestCase):

    layer = ZETTWERK_UI_THEMES_INTEGRATION_TESTING

    def test_registerResourceDirecotry_unregistered(self):
        ## even if it is called explicit it is not working without existing dir
        portal = self.layer['portal']
        abs_url = portal.absolute_url()
        res_url = '%s/++resource++zettwerk.ui.themes' % (abs_url)
        browser = Browser(portal)
        registerResourceDirectory('zettwerk.ui.themes', 'not_existing_dir')
        self.assertRaises(HTTPError,
                          browser.open,
                          res_url)

    def test_registerResourceDirecotry_registered(self):
        ## the resource gets registered on startup if the directory exists
        portal = self.layer['portal']
        abs_url = portal.absolute_url()
        res_url = '%s/++resource++zettwerk.ui.themes' % (abs_url)
        browser = Browser(portal)
        self.assertRaises(HTTPError,
                          browser.open,
                          res_url)
