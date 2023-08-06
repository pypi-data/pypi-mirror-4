#
# Tests for quintagroup.plonegooglesitemaps
#

from quintagroup.plonegooglesitemaps.tests.base import FunctionalTestCase
from StringIO import StringIO
from urllib import urlencode
import unittest

from Products.CMFPlone.utils import _createObjectByType


class TestConfigletSettings(FunctionalTestCase):

    def afterSetUp(self):
        super(TestConfigletSettings, self).afterSetUp()
        self.settingsURL = '/' + self.portal.absolute_url(1) + \
                           '/prefs_gsm_settings'

    def submitForm(self, fdata, fextra={}):
        form = {'form.submitted': 1}
        form.update(fdata)
        return self.publish(self.settingsURL, request_method='POST',
                            stdin=StringIO(urlencode(form)),
                            basic=self.auth, extra=fextra)

    def testInitButtons(self):
        settings = self.publish(self.settingsURL, self.auth).getBody()
        self.assert_("Add Content Sitemap" in settings)
        self.assert_("Add News Sitemap" in settings)
        self.assert_("Add Mobile Sitemap" in settings)

    def testAddContentSitemap(self):
        resp = self.submitForm({'form.button.AddContent':
                                "Add Content Sitemap"})
        self.assertEqual(resp.getStatus() / 100, 3)
        sm_edit = "sitemap.xml/edit"
        self.assertEqual(resp.getHeader("Location").endswith(sm_edit), True)
        # Add SM
        self.portal["sitemap.xml"]
        #self.portal["sitemap.xml"].setPortalTypes(("Documents",))
        newform = self.publish(self.settingsURL, basic=self.auth).getBody()
        self.assertEqual('href="http://nohost/plone/sitemap.xml/edit"' in
                         newform, True)
        self.assertEqual("form.button.AddContent" in newform, False)

    def testAddNewsSitemap(self):
        resp = self.submitForm({'form.button.AddNews': "Add News Sitemap"})
        self.assertEqual(resp.getStatus() / 100, 3)
        sm_edit = "news-sitemap.xml/edit"
        self.assertEqual(resp.getHeader("Location").endswith(sm_edit), True)
        # Add SM
        self.portal["news-sitemap.xml"]
        #self.portal["news-sitemap.xml"].setPortalTypes(("News Item",))
        newform = self.publish(self.settingsURL, basic=self.auth).getBody()
        self.assertEqual('href="http://nohost/plone/news-sitemap.xml/edit"'
                         in newform, True)
        self.assertEqual("form.button.AddNews" in newform, False)

    def testAddMobileSitemap(self):
        resp = self.submitForm({'form.button.AddMobile': "Add Mobile Sitemap"})
        self.assertEqual(resp.getStatus() / 100, 3)
        msm_edit = "mobile-sitemap.xml/edit"
        self.assertEqual(resp.getHeader("Location").endswith(msm_edit), True)
        # Add SM
        self.portal["mobile-sitemap.xml"]
        #self.portal["mobile-sitemap.xml"].setPortalTypes(("Documents",))
        newform = self.publish(self.settingsURL, basic=self.auth).getBody()
        self.assertEqual('href="http://nohost/plone/mobile-sitemap.xml/edit"'
                         in newform, True)
        self.assertEqual("form.button.AddMobile" in newform, False)


class TestConfigletOverview(FunctionalTestCase):

    def afterSetUp(self):
        super(TestConfigletOverview, self).afterSetUp()
        self.overviewURL = '/' + self.portal.absolute_url(1) + \
                           '/prefs_gsm_overview'
        self.smURL = "%s/sitemap.xml" % self.portal.absolute_url()

    def testInitial(self):
        overview = self.publish(self.overviewURL, self.auth).getBody()
        self.assert_(not self.smURL in overview)

    def testPresentedSM(self):
        _createObjectByType("Sitemap", self.portal, id="sitemap.xml",
                            sitemapType="content")
        overview = self.publish(self.overviewURL, self.auth).getBody()
        self.assert_(self.smURL in overview)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConfigletSettings))
    suite.addTest(unittest.makeSuite(TestConfigletOverview))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
#    framework()
