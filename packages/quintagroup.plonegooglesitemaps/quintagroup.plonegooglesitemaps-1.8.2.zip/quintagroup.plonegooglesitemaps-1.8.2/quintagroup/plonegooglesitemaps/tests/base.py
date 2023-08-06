#
# Tests for quintagroup.plonegooglesitemaps
#

from zope.interface import Interface
from zope.interface import alsoProvides
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.setup import portal_owner
from Products.PloneTestCase.setup import default_password

import quintagroup.plonegooglesitemaps
from quintagroup.plonegooglesitemaps.browser import mobilesitemapview
from quintagroup.plonegooglesitemaps.interfaces import IGoogleSitemapsLayer

from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer

quintagroup.plonegooglesitemaps.config.testing = 1
quintagroup.plonegooglesitemaps.config.UPDATE_CATALOG = True

PRODUCT = 'quintagroup.plonegooglesitemaps'


class NotInstalled(BasePTCLayer):
    """Initialize the package, without installation into portal
    """
    def afterSetUp(self):
        fiveconfigure.debug_mode = True
        import quintagroup.plonegooglesitemaps
        zcml.load_config('configure.zcml', quintagroup.plonegooglesitemaps)
        zcml.load_config('overrides.zcml', quintagroup.plonegooglesitemaps)
        fiveconfigure.debug_mode = False

        if not ptc.PLONE31:
            ztc.installProduct("plone.browserlayer")

        ztc.installPackage(PRODUCT)


class Installed(BasePTCLayer):
    """ Install product into the portal
    """
    def afterSetUp(self):
        if not ptc.PLONE31:
            self.addProduct("plone.browserlayer")
        self.addProduct(PRODUCT)


class UnInstalled(BasePTCLayer):
    """ UnInstall product from the portal
    """
    def afterSetUp(self):
        qi = getattr(self.portal, 'portal_quickinstaller', None)
        qi.uninstallProducts(products=[PRODUCT, ])


NotInstalledLayer = NotInstalled([ptc_layer, ])
InstalledLayer = Installed([NotInstalledLayer, ])
UnInstalledLayer = UnInstalled([InstalledLayer, ])


class IMobileMarker(Interface):
    """Test Marker interface for mobile objects"""


class MixinTestCase(object):
    """ Define layer and common afterSetup method with package installation.
        Package installation on plone site setup impossible because of
        five's registerPackage directive not recognized on module initializing.
    """
    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.workflow = self.portal.portal_workflow
        self.orig_mobile_ifaces = None
        alsoProvides(self.portal.REQUEST, IGoogleSitemapsLayer)

    def patchMobile(self):
        # patch mobile sitemap view
        self.orig_mobile_ifaces = mobilesitemapview.MOBILE_INTERFACES
        mobilesitemapview.MOBILE_INTERFACES = [IMobileMarker.__identifier__, ]

    def beforeTearDown(self):
        if getattr(self, 'orig_mobile_ifaces', None) is not None:
            mobilesitemapview.MOBILE_INTERFACES = self.orig_mobile_ifaces


class TestCaseNotInstalled(ptc.PloneTestCase):
    layer = NotInstalledLayer


class TestCase(ptc.PloneTestCase, MixinTestCase):
    layer = InstalledLayer

    def afterSetUp(self):
        ptc.PloneTestCase.afterSetUp(self)
        MixinTestCase.afterSetUp(self)

    def beforeTearDown(self):
        ptc.PloneTestCase.beforeTearDown(self)
        MixinTestCase.beforeTearDown(self)


class TestCaseUnInstalled(ptc.PloneTestCase):
    layer = UnInstalledLayer


class FunctionalTestCaseNotInstalled(ptc.FunctionalTestCase):
    layer = NotInstalledLayer


class FunctionalTestCase(ptc.FunctionalTestCase, MixinTestCase):
    layer = InstalledLayer

    def afterSetUp(self):
        ptc.FunctionalTestCase.afterSetUp(self)
        MixinTestCase.afterSetUp(self)
        self.auth = "%s:%s" % (portal_owner, default_password)

    def beforeTearDown(self):
        ptc.FunctionalTestCase.beforeTearDown(self)
        MixinTestCase.beforeTearDown(self)


class FunctionalTestCaseUnInstalled(ptc.FunctionalTestCase):
    layer = UnInstalledLayer
