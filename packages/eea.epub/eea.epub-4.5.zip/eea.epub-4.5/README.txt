EEA Epub product
================
A product which allows you to import in Plone epub files.

Contents
========

.. contents::


Introduction
============

EEA Epub product allows you to import in Plone epub files. On upload,
Epub content will imported as Plone folders, files, images and documents.

Export to Epub is also available.

As of version 4.3 epub files created with **Adobe InDesign CS4** and **Sigil** are tested and known
to work with this package, previous versions of this package only supported epubs created with InDesign.


Main features
=============

EEA Epub features:

  1. Imports epub files as Plone content.
  2. Stores the original epub in the main folder for easy retrieval.
  3. Exports the Plone content back into an epub.
  4. Clean filename as you import the epub and they contain characters that wouldn't be allowed
     as a Plone id. 
     This behaviour is on by default but it can be disabled by unchecking the boolean flag at portal_properties/site_properties
     'clean_epub_file_names'.
     If you find that the Document Pages added by the Epub process has broken links try to re-upload without this boolean flag.

Epub compatibility
==================

EEA Epub makes the following assumptions about the loaded epub:

  1. You don't use unicode or other special characters into the name of the epub, images or links
  2. You've created the epub with "Adobe InDesign CS4" or "Sigil" which uses some standards for the following:

    * The table of contents is named toc.ncx and is placed inside OEBPS
    * Book text & images are placed inside the folder OEBPS or other folders that are children of OEBPS
    * Items ids doesn't contain the following characters . / \ ( if possible stick to letters, numbers and - _ )

Best practices when creating an epub:

  1. Chapter names should not be all uppercase or use special characters
  2. Image names should not contain spaces, periods, / or other special characters

Debugging
=========

At this moment any errors that would appear on the site are surpressed with a info message.

If you want to see the detailed error check the Plone instance log usually found in buildout-folder/var/log.

Installation
============

The easiest way to get eea.epub support in Plone 4 using this
package is to work with installations based on `zc.buildout`_.
Other types of installations should also be possible, but might turn out
to be somewhat tricky.

To get started you will simply need to add the package to your "eggs" and
"zcml" sections, run buildout, restart your Plone instance and install the
"eea.epub" package using the quick-installer or via the "Add-on
Products" section in "Site Setup".

  .. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout/

You can download a sample buildout at:

  https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.epub/buildouts

Getting started
===============

From "Add new" menu select "EpubFile" and upload an epub file.

Dependecies
===========

  1. BeautifulSoup
  2. Lxml
  3. Plone 4.x


Live demo
=========

Here some live production demos at EEA (European Environment Agency)

  1. http://www.eea.europa.eu/soer/synthesis


Source code
===========

Latest source code (Plone 4 compatible):
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.epub/trunk

Plone 2 and 3 compatible:
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.epub/branches/plone25


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Epub (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Links
=====

  1. EEA Epub wiki page: https://svn.eionet.europa.eu/projects/Zope/wiki/HowToEpub


Funding
=======

  EEA_ - European Enviroment Agency (EU)

.. _EEA: http://www.eea.europa.eu/

