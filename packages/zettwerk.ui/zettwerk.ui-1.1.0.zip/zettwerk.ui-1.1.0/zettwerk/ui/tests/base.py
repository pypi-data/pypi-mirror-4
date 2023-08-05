import zettwerk.ui
import collective.js.jqueryui
import plone.app.theming

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.testing import z2

from gocept.selenium.plonetesting.testing_plone import selenium_layer

import os
import Globals
import shutil


class ZettwerkUI(PloneSandboxLayer):
    """ default plone layer, for tests, that depends on plone """

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=plone.app.theming)
        self.loadZCML(package=zettwerk.ui)
        self.loadZCML(package=collective.js.jqueryui)
        z2.installProduct(app, 'zettwerk.ui')
        z2.installProduct(app, 'collective.js.jqueryui')

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'zettwerk.ui:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'zettwerk.ui')


ZETTWERK_UI_FIXTURE = ZettwerkUI()
ZETTWERK_UI_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ZETTWERK_UI_FIXTURE,),
    name="ZettwerkUI:Integration"
    )


class ZettwerkUIThemes(PloneSandboxLayer):
    """ for tests, that depends on the themes directory """

    defaultBases = (ZETTWERK_UI_FIXTURE,)

    def testSetUp(self):
        """ we use this handle, cause we want a clean directory structure for
        every test """
        pwd = os.getcwd()
        fake_parts = os.path.join(pwd, 'parts')
        if not os.path.exists(fake_parts):
            os.mkdir(fake_parts)
        fake_instance = os.path.join(fake_parts, 'instance')
        if not os.path.exists(fake_instance):
            os.mkdir(fake_instance)
        setattr(Globals, 'INSTANCE_HOME', fake_instance)
        fake_downloads = os.path.join(pwd, 'zettwerk.ui.downloads')
        if not os.path.exists(fake_downloads):
            os.mkdir(fake_downloads)

    def testTearDown(self):
        """ we use this handle, cause we want a clean file structure for
        every test """
        pwd = os.getcwd()
        fake_parts = os.path.join(pwd, 'parts')
        if os.path.exists(fake_parts):
            shutil.rmtree(fake_parts)
        fake_downloads = os.path.join(pwd, 'zettwerk.ui.downloads')
        if os.path.exists(fake_downloads):
            shutil.rmtree(fake_downloads)


ZETTWERK_UI_THEMES_FIXTURE = ZettwerkUIThemes()
ZETTWERK_UI_THEMES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ZETTWERK_UI_THEMES_FIXTURE,),
    name="ZettwerkUIThemes:Integration"
    )


class ZettwerkUISelenium(PloneSandboxLayer):
    """ """

    defaultBases = (ZETTWERK_UI_THEMES_FIXTURE, selenium_layer)


ZETTWERK_UI_SELENIUM_FIXTURE = ZettwerkUISelenium()
ZETTWERK_UI_SELENIUM_TESTING = FunctionalTesting(
    bases=(ZETTWERK_UI_SELENIUM_FIXTURE,),
    name="ZettwerkUISelenium:Selenium"
    )
