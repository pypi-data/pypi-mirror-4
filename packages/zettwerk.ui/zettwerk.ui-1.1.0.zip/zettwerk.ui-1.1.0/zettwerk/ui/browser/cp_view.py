## ControlPanel form for the UITool

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets
from zope.app.form.browser import DisplayWidget
from zope.i18n import translate

from zope.component import adapts
from zope.interface import implements

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from ..tool.tool import IUITool, IUIToolTheme, \
    IUIToolThemeroller
from zettwerk.ui import messageFactory as _
from ..filesystem import isAvailable, DOWNLOAD_HOME


class UIControlPanelAdapter(SchemaAdapterBase):
    """ Adapter for the interface schema fields """

    adapts(IPloneSiteRoot)
    implements(IUITool)

    def __init__(self, context):
        super(UIControlPanelAdapter, self).__init__(context)
        self.portal = context
        ui_tool = getToolByName(self.portal, 'portal_ui_tool')
        self.context = ui_tool

theme = FormFieldsets(IUIToolTheme)
theme.id = 'theme'
theme.label = _(u"Theme")
theme.description = _(u'Select a theme from your downloaded themes.')

themeroller = FormFieldsets(IUIToolThemeroller)
themeroller.id = 'themeroller'
themeroller.label = _('Themeroller')
themeroller.description = _(u"theme_description_text", """New themes gets
downloaded to your server's filesystem. The target directory for storing them
is given below. If the folder is not available - downloading is disabled. But
this tool can create the directory. If you want to integrate a custom theme
from themeroller do not use the themeroller's download link - that will
download the theme to your local machine. You must use the save button below.
""")


class ThemerollerDisplayWidget(DisplayWidget):
    """ Display the themeroller link """

    def __call__(self):
        tool = self.context.context
        tool._rebuildThemeHashes()
        if tool.theme and tool.themeHashes:
            hash = tool.themeHashes.get(tool.theme, '')
            themeroller = u"javascript:callThemeroller('%s')" % (hash)
        else:
            themeroller = u"javascript:callThemeroller()"

        open_link = '<a href="%s">%s</a>' % (
            themeroller,
            translate(
                _(u"Open jquery.ui themeroller (only firefox)"),
                domain="zettwerk.ui",
                context=self.request
            )
        )
        themeroller_input = '<input type="hidden" name="form.themeroller" ' \
            'value="" />'
        create_help = translate(_(u"Create download directory at: "),
                                domain="zettwerk.ui",
                                context=self.request)
        create_text = "%s <br />%s" % (create_help, DOWNLOAD_HOME)
        create_dl = u'<a class="createDLD" ' \
            u'href="javascript:createDLDirectory()">%s</a>' % (create_text)

        if isAvailable():
            return '%s %s' % (open_link, themeroller_input)
        else:
            return create_dl


class UIControlPanel(ControlPanelForm):
    """ Build the ControlPanel form. """

    form_fields = FormFieldsets(theme, themeroller)

    form_fields['themeroller'].custom_widget = ThemerollerDisplayWidget
    form_fields['themeroller'].for_display = True

    label = _(u"Zettwerk UI Themer")
    description = _('cp_description',
                    u'With the theme link, you can choose ' \
                        u'a theme from your existing themes. The ' \
                        u'themeroller link is to create and change themes.'
                    )

    def _on_save(self, data):
        """ handle themeroller download """
        name = data.get('download', '')
        if name:
            ## why is form.themeroller not available via data?
            theme_hash = self.request.get('form.themeroller', '')
            if theme_hash:
                tool = self.context

                ## also note, that tool.theme gets set via tool directly
                tool.handleDownload(name, theme_hash)

                ## and reset the values, they are not needed anymore
                tool.download = ''
                tool.themeroller = ''
