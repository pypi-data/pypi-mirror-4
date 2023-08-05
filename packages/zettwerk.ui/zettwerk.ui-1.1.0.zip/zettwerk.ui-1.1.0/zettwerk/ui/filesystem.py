import os
import re
import zipfile
import fileinput
from stat import S_ISDIR, ST_MODE
import Globals

CSS_FILENAME = 'jquery-ui-.custom.css'
INSTANCE_HOME = getattr(Globals, 'INSTANCE_HOME', None)
if INSTANCE_HOME is not None:
    BUILDOUT_HOME = os.path.join(INSTANCE_HOME, '..', '..')
    DOWNLOAD_HOME = os.path.join(BUILDOUT_HOME, 'zettwerk.ui.downloads')
else:
    ## fail-safe when used without zope
    BUILDOUT_HOME = '.'
    DOWNLOAD_HOME = os.path.join(BUILDOUT_HOME, 'zettwerk.ui.downloads')


def isAvailable():
    """ """
    return os.path.exists(DOWNLOAD_HOME)


def createDownloadFolder():
    """ Create the download directory. """
    if not isAvailable():
        os.mkdir(DOWNLOAD_HOME)


def storeBinaryFile(name, content):
    """ """
    filepath = os.path.join(DOWNLOAD_HOME, '%s.zip' % (name))
    f = open(filepath, 'wb')
    f.write(content)
    f.close()


def extractZipFile(name):
    """ """
    if not os.path.exists(os.path.join(DOWNLOAD_HOME, name)):
        os.mkdir(os.path.join(DOWNLOAD_HOME, name))
    if not os.path.exists(os.path.join(DOWNLOAD_HOME, name, 'images')):
        os.mkdir(os.path.join(DOWNLOAD_HOME, name, 'images'))

    filename = '%s.zip' % (name)
    f = os.path.join(DOWNLOAD_HOME, filename)
    z = zipfile.ZipFile(f, 'r')
    for content in z.namelist():
        if content.find('css/custom-theme/') == 0:
            part = content.replace('css/custom-theme/', '')
            output = os.path.join(DOWNLOAD_HOME, name, part)
            getter = z.read(content)
            setter = file(output, 'wb')
            setter.write(getter)
            setter.close()
    z.close()


def getDirectoriesOfDownloadHome():
    """ return all directories of the download
    home folder. """
    dirs = []
    if isAvailable():
        for name in os.listdir(DOWNLOAD_HOME):
            if S_ISDIR(os.stat(os.path.join(DOWNLOAD_HOME, name))[ST_MODE]):
                dirs.append(name)
    return dirs


def getThemeHashOfCustomCSS(theme_dir):
    filepath = os.path.join(DOWNLOAD_HOME,
                            theme_dir,
                            CSS_FILENAME)
    reg = re.compile('visit http://jqueryui.com/themeroller/\?(.+)', re.S)

    if os.path.exists(filepath):
        for line in fileinput.input(filepath):
            match = reg.search(line)
            if match:
                fileinput.close()
                return match.group(1)
