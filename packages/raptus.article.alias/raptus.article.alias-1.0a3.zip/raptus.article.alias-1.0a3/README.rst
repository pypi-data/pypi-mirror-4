Introduction
============

Provides the possibility to create aliases for content objects which may be
contained in an article and display them in the specified components.

Dependencies
------------
    * raptus.article.core

Installation
============

Note if you install raptus.article.default you can skip this installation steps.

To install raptus.article.collections into your Plone instance, locate the file
buildout.cfg in the root of your Plone instance directory on the file system,
and open it in a text editor.

Add the actual raptus.article.alias add-on to the "eggs" section of
buildout.cfg. Look for the section that looks like this::

    eggs =
        Plone

This section might have additional lines if you have other add-ons already
installed. Just add the raptus.article.collections on a separate line, like this::

    eggs =
        Plone
        raptus.article.alias

Note that you have to run buildout like this::

    $ bin/buildout

Then go to the "Add-ons" control panel in Plone as an administrator, and
install or reinstall the "raptus.article.default" product.

Note that if you do not use the raptus.article.default package you have to
include the zcml of raptus.article.alias either by adding it
to the zcml list in your buildout or by including it in another package's
configure.zcml.

Copyright and credits
=====================

raptus.article is copyrighted by `Raptus AG <http://raptus.com>`_ and licensed under the GPL. 
See LICENSE.txt for details.
