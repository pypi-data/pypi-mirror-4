Introduction
============

zettwerk.ui integrates jquery.ui's themeroller into Plone 4.1. Themeroller is a tool to dynamically customize the jquery.ui css classes. For details about jquery.ui theming and themeroller see http://jqueryui.com/themeroller/.

See it in action: http://www.youtube.com/watch?v=p4_jU-5HUYA

Usage
=====

With this add-on it is very easy to adapt the look and color scheme of your plone site. After installation, there is a new extension product listed in the plone controlpanel which is called "Zettwerk UI Themer". Use the themes tab to create new themes via themeroller or apply one of the example themes from the themeroller gallery. Note that themeroller is only working in firefox, but the existing themes can be used with all browsers.

Feel free to contact us for feedback.

Technical background and pre 1.0 versions
=========================================

For versions below 1.0 zettwerk.ui made heavy use of javascript to manipulate the dom and css of the generated output page. This was ok for prototyping but probably not for production. Especially slower browsers shows some kind of flickering, till all manipulations were applied. With version 1.0, the complete concept to do most of the manipulation changed to xsl-transforms, applied via diazo / plone.app.theming. This results in a much better user experience. On the other hand, zettwerk.ui acts now as a skin (while the former one was none).

Installation
============

Add zettwerk.ui to your buildout eggs::

  eggs = ..
         zettwerk.ui

After running buildout and starting the instance, you can install Zettwerk UI Themer via portal_quickinstaller to your plone instance. zettwerk.ui requires Plone 4.1 cause it depends on `plone.app.theming <http://pypi.python.org/pypi/plone.app.theming>`_. If you want to use zettwerk.ui in Plone 4.0 you can also use `version 0.40 <http://pypi.python.org/pypi/zettwerk.ui/0.40>`_, which is the last one, (officially) supporting Plone 4.0.x.


Filesystem dependency
=====================

Created themes are downloaded to the servers filesystem. So a directory is needed, to store these files. At the moment, this is located always relative from your INSTANCE_HOME: ../../zettwerk.ui.downloads. In a common buildout environment, that is directly inside your buildout folder.

Deployment and reuse of themes
==============================

You can easily move the dowloaded themes from the download folder from one buildout instance to another. So to deploy a theme just copy the folder with the name of your theme from your develop server to your live server. It should be immediatelly available (without restart) - but only if the download folder was already created.
