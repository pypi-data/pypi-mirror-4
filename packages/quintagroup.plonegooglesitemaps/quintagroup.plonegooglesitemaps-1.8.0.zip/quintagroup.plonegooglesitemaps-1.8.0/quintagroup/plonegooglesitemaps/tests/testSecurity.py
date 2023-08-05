#
# Tests related to general Sitemap type.
#
from quintagroup.plonegooglesitemaps.tests.base \
    import FunctionalTestCase, IMobileMarker
from quintagroup.plonegooglesitemaps.tests.XMLParser import parse

import unittest
from zope.interface import alsoProvides
from Products.CMFPlone.utils import _createObjectByType


class MixinSecurity(FunctionalTestCase):

    def getview(self, vpath):
        return self.publish("/" + self.portal.absolute_url(1) +
                            "/" + vpath, self.auth)


class TestSecurityConfigletManager(MixinSecurity):

    def afterSetUp(self):
        super(TestSecurityConfigletManager, self).afterSetUp()
        self.auth = "admin:admin"
        self.portal.portal_membership.addMember('admin', 'admin',
                                                ('Manager',), [])

    def testConfigOverview(self):
        resp = self.getview("prefs_gsm_overview")
        self.assertEqual(resp.status / 100, 2)

    def testConfigSettings(self):
        resp = self.getview("prefs_gsm_settings")
        self.assertEqual(resp.status / 100, 2)

    def testConfigVerification(self):
        resp = self.getview("prefs_gsm_verification")
        self.assertEqual(resp.status / 100, 2)


class TestSecurityConfigletNotManager(MixinSecurity):

    def afterSetUp(self):
        super(TestSecurityConfigletNotManager, self).afterSetUp()
        self.auth = "mem:mem"
        self.portal.portal_membership.addMember('mem',
                                                'mem',
                                                ('Member',),
                                                [])

    def testConfigOverview(self):
        resp = self.getview("prefs_gsm_overview")
        self.assertNotEqual(resp.status / 100, 2)

    def testConfigSettings(self):
        resp = self.getview("prefs_gsm_settings")
        self.assertNotEqual(resp.status / 100, 2)

    def testConfigVerification(self):
        resp = self.getview("prefs_gsm_verification")
        self.assertNotEqual(resp.status / 100, 2)


SM_TYPES = {"content": {"id": "sitemap.xml", "types": ("Document",)},
            "news": {"id": "news-sitemap.xml", "types": ("News Item",)},
            "mobile": {"id": "mobile-sitemap.xml", "types": ("Document",)},
            }
from DateTime import DateTime


class TestSecuritySiteMaps(MixinSecurity):

    def afterSetUp(self):
        super(TestSecuritySiteMaps, self).afterSetUp()
        self.auth = ":"
        self.patchMobile()
        self.createSMaps()
        self.createContent()

    def createSMaps(self):
        self.smaps = {}
        for smtype, smdata in SM_TYPES.items():
            _createObjectByType("Sitemap", self.portal, id=smdata["id"],
                                sitemapType=smtype,
                                portalTypes=smdata["types"])
            sm = getattr(self.portal, smdata["id"])
            sm.at_post_create_script()
            self.smaps[smtype] = sm

    def createContent(self):
        self.my_doc = _createObjectByType('Document', self.portal, id='my_doc')
        self.workflow.doActionFor(self.my_doc, 'publish')
        self.my_news = _createObjectByType('News Item', self.portal,
                                           id='my_news')
        self.my_news.edit(title="My News Item (test)",
                          effectiveDate=DateTime().strftime("%Y-%m-%d"))
        self.workflow.doActionFor(self.my_news, 'publish')
        # mobile content must provides additional interfaces
        # to fall into mobile sitemap
        alsoProvides(self.my_doc, IMobileMarker)
        self.my_doc.reindexObject()
        self.my_news.reindexObject()

    def reparse(self, data):
        parsed = parse(data)
        return parsed["start"], parsed["data"]

    def testContentSM(self):
        resp = self.getview("sitemap.xml")
        self.assertEqual(resp.status / 100, 2)
        start, data = self.reparse(resp.getBody())
        self.assert_("loc" in start)
        self.assert_(self.my_doc.absolute_url() in data)

    def testNewsSM(self):
        resp = self.getview("news-sitemap.xml")
        self.assertEqual(resp.status / 100, 2)
        start, data = self.reparse(resp.getBody())
        self.assert_("n:name" in start)
        self.assert_("My News Item" in data)

    def testMobileSM(self):
        resp = self.getview("mobile-sitemap.xml")
        self.assertEqual(resp.status / 100, 2)
        start, data = self.reparse(resp.getBody())
        self.assert_("loc" in start)
        self.assert_(self.my_doc.absolute_url() in data)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSecurityConfigletManager))
    suite.addTest(unittest.makeSuite(TestSecurityConfigletNotManager))
    suite.addTest(unittest.makeSuite(TestSecuritySiteMaps))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
#    framework()
