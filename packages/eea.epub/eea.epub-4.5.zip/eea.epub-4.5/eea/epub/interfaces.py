""" Marker Iterfaces for Epub
"""
from zope.interface import Interface

class IImportedBook(Interface):
    """ Marker interface for epub root folder """

class IImportedChapter(Interface):
    """ Marker interface for each imported chapter """

class IExportable(Interface):
    """ Marker interface for all epub exporable content types """

class IImportedImage(Interface):
    """ Marker interface for imported epub images """
