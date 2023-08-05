from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from zope.component.globalregistry import getGlobalSiteManager
from zope.security.checker import CheckerPublic, NamesChecker
from zope.app.publisher.browser.directoryresource \
    import DirectoryResourceFactory
from zope.app.publisher.browser.resourcemeta import allowed_names
import logging
import os


def registerResourceDirectory(name, directory,
                              layer=IDefaultBrowserLayer,
                              permission='zope.Public'):
    """ This function registers a resource directory with global registry. """

    if os.path.exists(directory):
        logging.info('Registering %s as %s', directory, name)

        if permission == 'zope.Public':
            permission = CheckerPublic

        checker = NamesChecker(allowed_names + ('__getitem__', 'get'),
                               permission)

        factory = DirectoryResourceFactory(directory, checker, name)
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(factory, (layer,), Interface, name)
