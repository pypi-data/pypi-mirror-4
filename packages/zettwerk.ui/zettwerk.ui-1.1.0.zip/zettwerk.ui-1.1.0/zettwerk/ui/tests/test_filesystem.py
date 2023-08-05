import unittest
import os
import shutil
import zipfile

from base import ZETTWERK_UI_THEMES_INTEGRATION_TESTING

from zettwerk.ui.filesystem import isAvailable
from zettwerk.ui.filesystem import createDownloadFolder
from zettwerk.ui.filesystem import storeBinaryFile
from zettwerk.ui.filesystem import extractZipFile
from zettwerk.ui.filesystem import getDirectoriesOfDownloadHome
from zettwerk.ui.filesystem import getThemeHashOfCustomCSS


class TestResources(unittest.TestCase):

    layer = ZETTWERK_UI_THEMES_INTEGRATION_TESTING

    def test_isAvailable(self):
        self.assertTrue(isAvailable())

    def test_createDownloadHome(self):
        ## in the initial layer setup, its already available
        self.assertTrue(isAvailable())
        createDownloadFolder()
        self.assertTrue(isAvailable())

        ## so ne remove it
        pwd = os.getcwd()
        fake_downloads = os.path.join(pwd, 'zettwerk.ui.downloads')
        shutil.rmtree(fake_downloads)
        self.assertFalse(isAvailable())
        ## and let create it
        createDownloadFolder()
        self.assertTrue(isAvailable())

    def test_storeBinaryFile(self):
        from zettwerk.ui.filesystem import DOWNLOAD_HOME
        name = 'tester'
        filename = '%s.zip' % (name)
        path = os.path.join(DOWNLOAD_HOME, filename)
        self.assertFalse(os.path.exists(path))
        content = 'irrelevant'
        storeBinaryFile(name, content)
        self.assertTrue(os.path.exists(path))

    def test_extractZipFile(self):
        ## we first need a zipfile
        name = 'tester'
        filename = '%s.zip' % (name)
        from zettwerk.ui.filesystem import DOWNLOAD_HOME
        filepath = os.path.join(DOWNLOAD_HOME, filename)
        z = zipfile.ZipFile(filepath, 'w')
        content = 'irrelevant'
        z.writestr('css/custom-theme/something.css',
                   content)
        z.writestr('css/ignored.css',
                   content)
        z.close()

        extractZipFile(name)
        self.assertTrue(os.path.exists(os.path.join(DOWNLOAD_HOME, name)))
        self.assertTrue(os.path.exists(os.path.join(DOWNLOAD_HOME,
                                                    name,
                                                    'images')))
        self.assertTrue(os.path.exists(os.path.join(DOWNLOAD_HOME, filename)))
        self.assertFalse(os.path.exists(os.path.join(DOWNLOAD_HOME,
                                                    'ignored.css')))

    def test_getDirectoriesOfDownloadHome(self):
        self.assertEquals(getDirectoriesOfDownloadHome(), [])
        from zettwerk.ui.filesystem import DOWNLOAD_HOME
        os.mkdir(os.path.join(DOWNLOAD_HOME, 'folder'))
        self.assertEquals(getDirectoriesOfDownloadHome(), ['folder'])

        ## create a file to test, that only dirs are returned
        f = file(os.path.join(DOWNLOAD_HOME, 'file'), 'w')
        f.close()
        self.assertEquals(getDirectoriesOfDownloadHome(), ['folder'])

    def test_getThemeHashOfCustomCSS(self):
        ## prepare a test file
        from zettwerk.ui.filesystem import CSS_FILENAME
        from zettwerk.ui.filesystem import DOWNLOAD_HOME
        theme_dir = 'tester'
        os.mkdir(os.path.join(DOWNLOAD_HOME, theme_dir))
        f = file(os.path.join(DOWNLOAD_HOME, theme_dir, CSS_FILENAME), 'w')
        f.write("foo\n" * 10)
        f.write("bar\n" * 20)
        f.write(" * To view and modify this theme, visit ")
        f.write("http://jqueryui.com/themeroller/?hash=xxx\n")
        f.write("foo\n" * 20)
        f.close()
        ## first test with a wrong theme dir
        self.failIf(getThemeHashOfCustomCSS('not_existing'))
        ## then with the given above
        self.assertEquals(getThemeHashOfCustomCSS(theme_dir).strip(),
                          'hash=xxx')
