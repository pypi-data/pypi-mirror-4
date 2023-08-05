from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import UniqueObject, getToolByName
from OFS.SimpleItem import SimpleItem
from persistent.mapping import PersistentMapping

from zope.interface import Interface
from zope.interface import implements
from zope import schema
from zope.i18n import translate

from zettwerk.ui import messageFactory as _

import urllib2
from urllib import urlencode
import zipfile

from ..filesystem import extractZipFile, storeBinaryFile, \
    createDownloadFolder, getDirectoriesOfDownloadHome, \
    getThemeHashOfCustomCSS
from ..resources import registerResourceDirectory
from ..filesystem import DOWNLOAD_HOME

UI_DOWNLOAD_URL = 'http://jqueryui.com/download'

## a list of jquery.ui elements, needed for the url to download a new theme.
UI = """ui.core.js
ui.widget.js
ui.mouse.js
ui.position.js
ui.draggable.js
ui.droppable.js
ui.resizable.js
ui.selectable.js
ui.sortable.js
ui.accordion.js
ui.autocomplete.js
ui.button.js
ui.dialog.js
ui.slider.js
ui.tabs.js
ui.datepicker.js
ui.progressbar.js
effects.core.js
effects.blind.js
effects.bounce.js
effects.clip.js
effects.drop.js
effects.explode.js
effects.fold.js
effects.highlight.js
effects.pulsate.js
effects.scale.js
effects.shake.js
effects.slide.js
effects.transfer.js"""


class IUIToolTheme(Interface):
    """ UITool interface defining needed schema fields. """

    theme = schema.Choice(title=_(u"Theme"),
                          required=False,
                          vocabulary="zettwerk.ui.ListThemesVocabulary")


class IUIToolThemeroller(Interface):
    """ UITool interface for themeroller fields """

    themeroller = schema.TextLine(
        title=_("Themeroller")
        )

    download = schema.TextLine(
        title=_("Download"),
        required=False,
        description=_("Name of the theme to download.")
        )


class IUITool(IUIToolTheme, IUIToolThemeroller):
    """ Mixin Interface """
    pass


class UITool(UniqueObject, SimpleItem):
    """ The UITool handles creation and loading of ui themes. """

    implements(IUITool)
    id = 'portal_ui_tool'

    ## implement the fields, given through the interfaces
    theme = ''
    download = ''
    themeroller = ''
    themeHashes = None

    def cp_js_translations(self):
        """ return some translated js strings """
        return u'var sorry_only_firefox = "%s";\n' \
            u'var nothing_themed = "%s";\n' \
            u'var name_missing = "%s";\n' \
            u'var no_sunburst_name = "%s";\n' \
            u'var no_special_chars = "%s";\n\n' % (
            translate(_(u"Sorry, due to security restrictions, this tool " \
                            u"only works in Firefox"),
                      domain='zettwerk.ui',
                      context=self.REQUEST),
            translate(_(u"Download name given but nothing themed - please " \
                            "use themeroller"),
                      domain='zettwerk.ui',
                      context=self.REQUEST),
            translate(_(u"You opened themeroller, but no download name is " \
                            u"given. Click ok to continue and ignore your " \
                            u"changes or click cancel to enter a name."),
                      domain='zettwerk.ui',
                      context=self.REQUEST),
            translate(_(u"Sorry, sunburst is an invalid name"),
                      domain='zettwerk.ui',
                      context=self.REQUEST),
            translate(_(u"Please use no special characters."),
                      domain='zettwerk.ui',
                      context=self.REQUEST),
            )

    def css(self, *args):
        """ Generate the css rules, suitable for the given settings. """
        content_type_header = 'text/css;charset=UTF-8'
        self.REQUEST.RESPONSE.setHeader('content-type',
                                        content_type_header)
        result = ""

        if self.theme:
            ## the sunburst resource in portal_css is disabled
            ## cause enable/disabling resources in service mode
            ## seems not to work as i expect
            if self.theme == u'sunburst':
                result += '@import "++resource++jquery-ui-themes/' \
                    'sunburst/jqueryui.css";'
            else:
                resource_base = '++resource++zettwerk.ui.themes'
                result += '@import "%s/%s/jquery-ui-.custom.css";' % (
                    resource_base,
                    self.theme
                    )

        return result

    def _redirectToCPView(self, msg=None):
        """ Just a redirect. """
        if msg is not None:
            utils = getToolByName(self, 'plone_utils')
            utils.addPortalMessage(msg)

        portal_url = getToolByName(self, 'portal_url')
        url = '%s/%s/@@ui-controlpanel' % (portal_url(),
                                           self.getId())
        return self.REQUEST.RESPONSE.redirect(url)

    def _rebuildThemeHashes(self):
        """ For edit existing themes, the hash is needed. They are stored
        in self.themeHashes. The problem with this: by quick-reinstalling
        zettwerk.ui this attribute get None. Also, if new themes were
        copied 'by hand' (as described in the README for deploying) the
        themeHashes doesn't know the copied theme's hash. This method
        reads all available themes and the theme-custom.css file to rebuild
        the themeHashes attribute. Its called every time the control panel
        view is called. """
        if self.themeHashes is None:
            self.themeHashes = PersistentMapping()

        theme_dirs = getDirectoriesOfDownloadHome()
        for theme_dir in theme_dirs:
            theme_hash = getThemeHashOfCustomCSS(theme_dir)
            if theme_hash:
                self.themeHashes.update({theme_dir: theme_hash})
        self._handleSunburst()

    def _handleSunburst(self):
        """" since we support collective.js.jqueryui, it would make
        sense to add the provided sunburst theme as a theme, too. """
        ## no, i don't want to pep8-ify this string
        self.themeHashes.update(
            {'sunburst': '?ffDefault=%20Arial,FreeSans,sans-serif&fwDefault=normal&fsDefault=0.9em&cornerRadius=5px&bgColorHeader=dddddd&bgTextureHeader=01_flat.png&bgImgOpacityHeader=75&borderColorHeader=cccccc&fcHeader=444444&iconColorHeader=205c90&bgColorContent=ffffff&bgTextureContent=01_flat.png&bgImgOpacityContent=100&borderColorContent=cccccc&fcContent=444444&iconColorContent=205c90&bgColorDefault=205c90&bgTextureDefault=01_flat.png&bgImgOpacityDefault=45&borderColorDefault=cccccc&fcDefault=ffffff&iconColorDefault=ffffff&bgColorHover=dddddd&bgTextureHover=01_flat.png&bgImgOpacityHover=75&borderColorHover=448dae&fcHover=444444&iconColorHover=444444&bgColorActive=75ad0a&bgTextureActive=01_flat.png&bgImgOpacityActive=50&borderColorActive=cccccc&fcActive=ffffff&iconColorActive=ffffff&bgColorHighlight=ffdd77&bgTextureHighlight=01_flat.png&bgImgOpacityHighlight=55&borderColorHighlight=dd8800&fcHighlight=000000&iconColorHighlight=dd8800&bgColorError=ffddcc&bgTextureError=01_flat.png&bgImgOpacityError=45&borderColorError=dd0000&fcError=000000&iconColorError=dd0000&bgColorOverlay=aaaaaa&bgTextureOverlay=01_flat.png&bgImgOpacityOverlay=75&opacityOverlay=30&bgColorShadow=999999&bgTextureShadow=01_flat.png&bgImgOpacityShadow=55&opacityShadow=45&thicknessShadow=0px&offsetTopShadow=5px&offsetLeftShadow=5px&cornerRadiusShadow=5px'}
            )

    def createDLDirectory(self):
        """ Create the storage and register the resource"""
        createDownloadFolder()
        registerResourceDirectory(name='zettwerk.ui.themes',
                                  directory=DOWNLOAD_HOME)
        self._redirectToCPView(_(u"Directory created"))

    def handleDownload(self, name, hash):
        """ Download a new theme, created by themeroller.

        @param name: string with the name of the new theme.
        @param hash: themeroller hash, with theme settings.
        """

        url = self._prepareUIDownloadUrl(hash)
        handler = urllib2.urlopen(url)
        content = handler.read()
        storeBinaryFile(name, content)
        self._enableNewTheme(name, hash)

    def _enableNewTheme(self, name, hash):
        """ Extract the downloaded theme and set it as current theme. """
        try:
            extractZipFile(name)
        except zipfile.BadZipfile:
            ## This might fail as mentioned by Jensens
            ## mostly caused by the themeroller webservice
            IStatusMessage(self.REQUEST) \
                .addStatusMessage(
                _(u'The downloaded zipfile is corrupt. This could mean ' \
                      u'that the themeroller webservice has problems. The ' \
                      u'common fix for this is, to wait a day or two and ' \
                      'try it again.'),
                "error")
            return

        if self.themeHashes is None:
            self.themeHashes = PersistentMapping()

        self.themeHashes.update({name: hash})
        self.theme = name

    def _prepareUIDownloadUrl(self, hash):
        """ Built the download url. """

        data = []
        data.append(('download', 'true'))
        for part in UI.split('\n'):
            part = part.strip()
            if part:
                data.append(('files[]', part))
        data.append(('theme', '?' + hash))
        data.append(('scope', ''))
        data.append(('t-name', 'custom-theme'))
        data.append(('ui-version', '1.8'))

        data = urlencode(data)
        return "%s?%s" % (UI_DOWNLOAD_URL, data)
