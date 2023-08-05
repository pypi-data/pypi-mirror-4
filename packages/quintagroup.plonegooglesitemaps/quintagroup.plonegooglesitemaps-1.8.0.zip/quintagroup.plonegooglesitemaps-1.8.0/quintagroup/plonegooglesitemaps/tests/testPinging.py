from quintagroup.plonegooglesitemaps.tests.base import FunctionalTestCase
import sys
from StringIO import StringIO
import unittest

from Products.CMFPlone.utils import _createObjectByType


class TestPinging(FunctionalTestCase):

    def afterSetUp(self):
        super(TestPinging, self).afterSetUp()
        workflow = "simple_publication_workflow"
        self.workflow.setChainForPortalTypes(pt_names=('News Item',
                                                       'Document'),
                                             chain=workflow)
        gsm_properties = 'googlesitemap_properties'
        self.gsm_props = self.portal.portal_properties[gsm_properties]
        # Add sitemaps
        self.contentSM = _createObjectByType('Sitemap', self.portal,
                                             id='google-sitemaps')
        spw_publish = 'simple_publication_workflow#publish'
        self.contentSM.setPingTransitions((spw_publish,))
        self.newsSM = _createObjectByType('Sitemap', self.portal,
                                          id='news-sitemaps')
        self.newsSM.setPortalTypes(('News Item', 'Document'))
        self.newsSM.setPingTransitions((spw_publish,))
        self.sitemapUrl = '/' + self.portal.absolute_url(1) + \
                          '/google-sitemaps'
        # Add testing document to portal
        self.my_doc = _createObjectByType('Document', self.portal, id='my_doc')
        self.my_news = _createObjectByType('News Item', self.portal,
                                           id='my_news')

    def testAutomatePinging(self):
        # 1. Check for pinging both sitemaps
        back_out, myout = sys.stdout, StringIO()
        sys.stdout = myout
        try:
            self.workflow.doActionFor(self.my_doc, 'publish')
            myout.seek(0)
            data = myout.read()
        finally:
            sys.stdout = back_out

        self.assert_('Pinged %s sitemap to Google'
                     % self.contentSM.absolute_url() in data,
                     "Not pinged %s: '%s'" % (self.contentSM.id, data))
        self.assert_('Pinged %s sitemap to Google'
                     % self.newsSM.absolute_url() in data,
                     "Not pinged %s: '%s'" % (self.newsSM.id, data))

        # 2. Check for pinging only news-sitemap sitemaps
        back_out, myout = sys.stdout, StringIO()
        sys.stdout = myout
        try:
            self.workflow.doActionFor(self.my_news, 'publish')
            myout.seek(0)
            data = myout.read()
        finally:
            sys.stdout = back_out

        self.assert_('Pinged %s sitemap to Google'
                     % self.newsSM.absolute_url() in data,
                     "Not pinged %s: '%s'" % (self.newsSM.id, data))
        self.assert_(not 'Pinged %s sitemap to Google'
                     % self.contentSM.absolute_url() in data,
                     "Pinged %s on news: '%s'" % (self.contentSM.id, data))

    def testPingingWithSetupForm(self):
        # Ping news and content sitemaps
        formUrl = '/' + self.portal.absolute_url(1) + '/prefs_gsm_settings'
        qs = 'smselected:list=%s&smselected:list=%s&form.button.Ping=1' \
             '&form.submitted=1' % (self.contentSM.id, self.newsSM.id)

        back_out, myout = sys.stdout, StringIO()
        sys.stdout = myout
        try:
            self.publish("%s?%s" % (formUrl, qs), basic=self.auth)
            myout.seek(0)
            data = myout.read()
        finally:
            sys.stdout = back_out

        self.assert_('Pinged %s sitemap to Google'
                     % self.contentSM.absolute_url() in data,
                     "Not pinged %s: '%s'" % (self.contentSM.id, data))
        self.assert_('Pinged %s sitemap to Google'
                     % self.newsSM.absolute_url() in data,
                     "Not pinged %s: '%s'" % (self.newsSM.id, data))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPinging))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
#    framework()
