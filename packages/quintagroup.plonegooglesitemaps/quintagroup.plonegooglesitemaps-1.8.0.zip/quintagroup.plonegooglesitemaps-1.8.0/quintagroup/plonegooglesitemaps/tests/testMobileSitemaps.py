from quintagroup.plonegooglesitemaps.tests.base import TestCase, \
    FunctionalTestCase, IMobileMarker
from Products.PloneTestCase.setup import portal_owner, default_password
from quintagroup.plonegooglesitemaps.tests.XMLParser import parse
import unittest

from DateTime import DateTime

from zope.interface import alsoProvides
from zope.component import queryMultiAdapter

from Products.CMFPlone.utils import _createObjectByType

from quintagroup.plonegooglesitemaps.browser import mobilesitemapview
from quintagroup.plonegooglesitemaps.browser.commonview \
    import CommonSitemapView
from quintagroup.plonegooglesitemaps.browser.mobilesitemapview \
    import MobileSitemapView


class TestMobileSitemapsXML(FunctionalTestCase):

    def afterSetUp(self):
        super(TestMobileSitemapsXML, self).afterSetUp()
        self.patchMobile()
        _createObjectByType("Sitemap", self.portal, id="mobile-sitemap.xml",
                            sitemapType="mobile", portalTypes=("Document",))
        self.portal["mobile-sitemap.xml"].at_post_create_script()
        # Add testing mobile item to portal
        self.pubdate = (DateTime() + 1).strftime("%Y-%m-%d")
        self.my_mobile = _createObjectByType('Document', self.portal,
                                             id='my_mobile')
        alsoProvides(self.my_mobile, IMobileMarker)
        self.my_mobile.edit(text="Test mobile item",
                            title="First mobile (test)",
                            effectiveDate=self.pubdate)
        self.workflow.doActionFor(self.my_mobile, "publish")
        self.reParse()

    def reParse(self):
        # Parse mobile sitemap
        self.sitemap = self.publish("/" + self.portal.absolute_url(1) +
                                    "/mobile-sitemap.xml",
                                    "%s:%s" % (portal_owner,
                                               default_password)).getBody()
        parsed_sitemap = parse(self.sitemap)
        self.start = parsed_sitemap["start"]
        self.data = parsed_sitemap["data"]

    def test_urlset(self):
        self.assert_("urlset" in self.start.keys())
        urlset = self.start["urlset"]
        self.assertEqual(urlset.get("xmlns", ""),
                         "http://www.sitemaps.org/schemas/sitemap/0.9")
        self.assertEqual(urlset.get("xmlns:mobile", ""),
                         "http://www.google.com/schemas/sitemap-mobile/1.0")

    def test_url(self):
        self.assert_("url" in self.start.keys())

    def test_loc(self):
        self.assert_("loc" in self.start.keys())
        self.assert_(self.portal.absolute_url() + "/my_mobile" in self.data)

    def test_lastmod(self):
        md = [f for k, f in
              mobilesitemapview.MobileSitemapView.additional_maps
              if k == 'modification_date'][0]
        bmobile = self.portal.portal_catalog(id="my_mobile")[0]
        self.assert_("lastmod" in self.start.keys())
        self.assert_(md(bmobile) in self.data, "Wrong 'modified date':"
                     " must be '%s', but exist: '%s'"
                     % (md(bmobile), self.data))


class TestMobileSitemaps(TestCase):

    def afterSetUp(self):
        super(TestMobileSitemaps, self).afterSetUp()
        # create mobile sitemap
        _createObjectByType("Sitemap", self.portal, id="mobile-sitemap.xml",
                            sitemapType="mobile", portalTypes=("Document",))
        mobile_sm = self.portal["mobile-sitemap.xml"]
        mobile_sm.at_post_create_script()
        self.default_layout = mobile_sm.getProperty('layout', "")
        self.mobile_view = queryMultiAdapter((mobile_sm, self.portal.REQUEST),
                                             name=self.default_layout)

    def testLayout(self):
        self.assert_(self.default_layout == "mobile-sitemap.xml")

    def testInterface(self):
        sm_view = mobilesitemapview.ISitemapView
        self.assert_(sm_view.providedBy(self.mobile_view))

    def testClasses(self):
        self.assert_(isinstance(self.mobile_view, MobileSitemapView))
        self.assert_(isinstance(self.mobile_view, CommonSitemapView))

    def testAdditionalMaps(self):
        self.assert_(hasattr(self.mobile_view, "additional_maps"))
        self.assert_([1 for k, f in self.mobile_view.additional_maps
                      if k == "modification_date"])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMobileSitemapsXML))
    suite.addTest(unittest.makeSuite(TestMobileSitemaps))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
#    framework()
