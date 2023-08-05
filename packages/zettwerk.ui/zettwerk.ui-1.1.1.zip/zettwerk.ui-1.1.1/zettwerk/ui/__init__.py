# -*- extra stuff goes here -*-

from zope.i18nmessageid import MessageFactory
messageFactory = MessageFactory('zettwerk.ui')

## dynamic resource registration
from resources import registerResourceDirectory
from filesystem import DOWNLOAD_HOME
registerResourceDirectory(name='zettwerk.ui.themes',
                          directory=DOWNLOAD_HOME)

from Products.CMFCore import utils
from tool.tool import UITool


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    utils.ToolInit('Zettwerk UI Tool', tools=(UITool, ),
                   icon='z.png'
                   ).initialize(context)
