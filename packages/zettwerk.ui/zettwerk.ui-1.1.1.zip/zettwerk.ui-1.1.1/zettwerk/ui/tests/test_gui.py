import unittest
import time

from base import ZETTWERK_UI_SELENIUM_TESTING

from plone.app.testing.layers import SITE_OWNER_NAME
from plone.app.testing.layers import SITE_OWNER_PASSWORD


class TestGUI(unittest.TestCase):
    """ this tests also implicit the transform rules, by quering
    some of our custom css ids """

    layer = ZETTWERK_UI_SELENIUM_TESTING

    def test_enabled_elements_anonymous(self):
        """ check some important elements for ui classes """
        sel = self.layer['selenium']
        sel.open('/plone')

        ## footer
        result = sel.getAttribute("css=#portal-footer-ui @class")
        self.assertEquals(result, u'ui-state-active ui-corner-all')

        ## globalnav
        result = sel.getAttribute("css=#portal-globalnav-ui @class")
        self.assertEquals(result, u'ui-state-default ui-corner-all')

        ## personaltools
        result = sel.getAttribute("css=#portal-personaltools-ui @class")
        self.assertTrue(result.find('ui-state-default') != -1)

    def test_enabled_elements_authenticated(self):
        """ check some important elements for ui classes """
        sel = self.layer['selenium']
        sel.open('/plone')

        ## login
        sel.click('link=Log in')
        sel.waitForElementPresent('name=__ac_name')
        sel.type('name=__ac_name', SITE_OWNER_NAME)
        sel.type('name=__ac_password', SITE_OWNER_PASSWORD)
        sel.click('name=submit')
        sel.waitForPageToLoad()
        time.sleep(2)  # without this, the next call will fail (sometimes)

        ## edit-bar
        result = sel.getAttribute("css=#edit-bar-ui @id")
        self.assertEquals(result, u'edit-bar-ui')
        sel.open('/plone/logout')
        sel.waitForPageToLoad()

    def test_themeroller(self):
        ## themeroller is only working with firefox
        sel = self.layer['selenium']
        if sel.selenium.browserStartCommand != '*firefox':
            return

        ## login
        sel.open('/plone')
        sel.click('link=Log in')
        sel.waitForElementPresent('name=__ac_name')
        sel.type('name=__ac_name', SITE_OWNER_NAME)
        sel.type('name=__ac_password', SITE_OWNER_PASSWORD)
        sel.click('name=submit')
        sel.waitForPageToLoad()

        ## switch to the themeroller gui
        sel.open('/plone/portal_ui_tool/@@ui-controlpanel')
        sel.waitForPageToLoad()

        ## click themeroller fieldset
        sel.click("//form[@id='zc.page.browser_form']/div[1]/ul/li[2]/a/span")
        ## click themeroller link
        sel.click("link=Open jquery.ui themeroller (only firefox)")
        time.sleep(5)  # selenium's wait_for_frame_to_load not triggering

        ## open the gallery and choose an existing theme
        sel.click("link=Gallery")
        sel.click("//img[@alt='Sunny']")
        time.sleep(2)

        ## save the theme
        sel.type('name=form.download', 'tester')
        sel.click("form.actions.save")
        sel.waitForPageToLoad()

        ## click themes fieldset
        sel.click("//form[@id='zc.page.browser_form']/div[1]/ul/li[1]/a/span")
        ## and check the selected theme
        self.assertEquals(sel.getValue('form.theme'),
                          u'tester')
        sel.open('/plone/logout')
        sel.waitForPageToLoad()
