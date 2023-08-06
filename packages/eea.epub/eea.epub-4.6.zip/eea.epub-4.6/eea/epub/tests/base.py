""" Base module for epub tests
"""

from Products.Five import fiveconfigure as metaconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Zope2.App.zcml import load_config
import eea.epub

@onsetup
def setup_epub():
    """ setup epub test
    """
    metaconfigure.debug_mode = True
    load_config('configure.zcml', eea.epub)
    metaconfigure.debug_mode = False

setup_epub()
PloneTestCase.setupPloneSite(extension_profiles=('eea.epub:default',))


class EpubFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ EpubFunctionalTestCase class
    """
    pass
