from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc

from Products.Archetypes import public as atapi
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.setup import default_password, portal_owner


@onsetup
def setup_linkchecker_policy():
    ztc.installProduct('Five')

    fiveconfigure.debug_mode = True
    import gocept.linkchecker
    zcml.load_config('configure.zcml', gocept.linkchecker)
    fiveconfigure.debug_mode = False

    ztc.installPackage('gocept.linkchecker')
    ztc.installProduct('ZCatalog')


setup_linkchecker_policy()
ptc.setupPloneSite(products=['gocept.linkchecker'])


class LinkCheckerTestCase(ptc.FunctionalTestCase):

    def __init__(self, *args, **kw):
        super(LinkCheckerTestCase, self).__init__(*args, **kw)
        self.portal_owner = portal_owner
        self.default_password = default_password
