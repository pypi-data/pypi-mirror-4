from Products.CMFCore.utils import getToolByName


def uninstall(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-zettwerk.ui:uninstall')

    cp_tool = getToolByName(portal, 'portal_controlpanel')
    cp_tool.unregisterConfiglet('zettwerkui')

    return "Ran all uninstall steps."
