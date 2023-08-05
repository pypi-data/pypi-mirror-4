# $Id: functional.py 7848 2010-10-18 15:09:36Z karen $

'''
Functional tests base for zkaffold.
'''

__author__ = 'Karen Chan <karen@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision: 7848 $'[11:-2]

from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_package():
    fiveconfigure.debug_mode = True
    import zkaffold
    zcml.load_config('configure.zcml', zkaffold)
    fiveconfigure.debug_mode = False
    ztc.installPackage('zkaffold')

setup_package()
ptc.setupPloneSite(extension_profiles=(
    'zkaffold:default',
))

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional tests
    """
