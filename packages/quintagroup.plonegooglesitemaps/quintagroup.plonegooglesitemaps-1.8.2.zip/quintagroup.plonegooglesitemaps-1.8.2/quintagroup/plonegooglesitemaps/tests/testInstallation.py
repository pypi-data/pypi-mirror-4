from quintagroup.plonegooglesitemaps.config import SUPPORT_BLAYER
from quintagroup.plonegooglesitemaps.tests.base import TestCase, \
    PRODUCT, IGoogleSitemapsLayer
import unittest

from zope.component import getSiteManager
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.CMFPlone.utils import _createObjectByType
from quintagroup.canonicalpath.interfaces import ICanonicalLink


class TestGoogleSitemapsInstallation(TestCase):

    def testType(self):
        pt = self.portal.portal_types
        self.assert_('Sitemap' in pt.objectIds(),
                     'No "Sitemap" type after installation')
        #Test views
        views = pt.getTypeInfo('Sitemap').view_methods
        self.assert_('sitemap.xml' in views,
                     'No "sitemap.xml" view for Sitemap type')
        self.assert_('mobile-sitemap.xml' in views,
                     'No "mobile-sitemap.xml" view for Sitemap type')
        self.assert_('news-sitemap.xml' in views,
                     'No "news-sitemap.xml" view for Sitemap type')

    def testGSMProperties(self):
        pp = self.portal.portal_properties

        # Test types_not_searched
        self.assert_("Sitemap" in
                     pp['site_properties'].getProperty('types_not_searched'),
                     'No "Sitemap" added to types not searched '
                     'on installation')
        # Test metaTypesNotToList
        self.assert_("Sitemap" in
                     pp['navtree_properties'].
                     getProperty('metaTypesNotToList'),
                     'No "Sitemap" added to types not to '
                     'list on installation')

        # Test 'googlesitemap_properties'
        self.assert_('googlesitemap_properties' in pp.objectIds(),
                     'No "googlesitemap_properties" after installation')
        qsmprops = pp['googlesitemap_properties']
        self.assert_(qsmprops.hasProperty('verification_filenames'),
                     'No "verification_filenames" property added on '
                     'installation')

    def testSkins(self):
        ps = self.portal.portal_skins
        self.assert_('plonegooglesitemaps' in ps.objectIds(),
                     'No "plonegooglesitemaps" skin '
                     'layer in portal_skins')
        self.assert_('plonegooglesitemaps' in
                     ps.getSkinPath(ps.getDefaultSkin()),
                     'No "plonegooglesitemaps" skin layer '
                     'in default skin')

    def testConfiglet(self):
        cp = self.portal.portal_controlpanel
        self.assert_([1 for ai in cp.listActionInfos()
                     if ai['id'] == 'GoogleSitemaps'],
                     'No "GoogleSitemaps" configlet '
                     'added to plone control panel')

    def testNewsSchemaExtenderRegistered(self):
        lsm = getSiteManager(self.portal)
        news = self.portal.invokeFactory("News Item", id="test_news")
        news = getattr(self.portal, "test_news")
        adapter = "quintagroup.plonegooglesitemaps.newssitemapextender"
        self.assertNotEqual(lsm.queryAdapter(news,
                                             interface=ISchemaExtender,
                                             name=adapter),
                            None)

    def testUpdateCatalog(self):
        # Test added new columns in catalog
        Language = 'test_language'
        gsm_access = 'test_gsm_access'
        gsm_genres = (u'test_gsm_genres',)
        gsm_stock = 'test_gsm_stock'
        cols = ["canonical_link", "Language", "gsm_access",
                "gsm_genres", "gsm_stock"]
        getSiteManager(self.portal)
        catalog = self.portal.portal_catalog
        setuptools = self.portal.portal_setup
        for col in cols:
            self.assertEqual(col in catalog._catalog.names, True)

        # Test update catalog
        # Create news
        news = _createObjectByType('News Item', self.portal, id='test_news')
        news_cpath = "/my_test_news"
        news_clink = self.portal.absolute_url() + news_cpath

        # The canonical_link, Language, gsm_access, gsm_genres, gsm_stock
        # brain must contains not updated canonical_link data
        brain = catalog(id="test_news")[0]
        self.assertNotEqual(brain.canonical_link, news_clink)
        self.assertNotEqual(brain.Language, Language)
        self.assertNotEqual(brain.gsm_access, gsm_access)
        self.assertNotEqual(brain.gsm_genres, gsm_genres)
        self.assertNotEqual(brain.gsm_stock, gsm_stock)

        # Update fields
        ICanonicalLink(news).canonical_link = news_clink
        news.update(
            language=Language, gsm_access=gsm_access,
            gsm_genres=gsm_genres, gsm_stock=gsm_stock)
        setuptools.runImportStepFromProfile(
            'profile-quintagroup.plonegooglesitemaps:default', 'catalog')

        # The canonical_link, Language, gsm_access, gsm_genres, gsm_stock
        # brain must contains updated canonical_link data
        brain = catalog(id="test_news")[0]
        self.assertEqual(brain.canonical_link, news_clink)
        self.assertEqual(brain.Language, Language)
        self.assertEqual(brain.gsm_access, gsm_access)
        self.assertEqual(brain.gsm_genres, gsm_genres)
        self.assertEqual(brain.gsm_stock, gsm_stock)

    def test_browser_layer(self):
        if not SUPPORT_BLAYER:
            return

        from plone.browserlayer import utils
        self.assert_(IGoogleSitemapsLayer in utils.registered_layers(),
                     "Not registered 'IGoogleSitemapsLayer' browser layer")


class TestGoogleSitemapsUninstallation(TestCase):

    def afterSetUp(self):
        super(TestGoogleSitemapsUninstallation, self).afterSetUp()
        self.portal.portal_quickinstaller.uninstallProducts(
            products=['quintagroup.plonegooglesitemaps', ])
        self._refreshSkinData()

    def testNewsSchemaExtenderUnregistered(self):
        lsm = getSiteManager(self.portal)
        news = self.portal.invokeFactory("News Item", id="test_news")
        news = getattr(self.portal, "test_news")
        self.assertEqual(lsm.queryAdapter(news, interface=ISchemaExtender),
                         None)

    def testConfigletUninstall(self):
        self.assertNotEqual(
            self.portal.portal_quickinstaller.isProductInstalled(PRODUCT),
            True, '%s is already installed' % PRODUCT)
        configTool = self.portal.portal_controlpanel
        self.assertEqual('GoogleSitemaps' in [a.getId() for a in
                                              configTool.listActions()],
                         False,
                         'Configlet found after uninstallation')

    def test_browserlayer_uninstall(self):
        if not SUPPORT_BLAYER:
            return

        from plone.browserlayer import utils
        self.assertEqual(IGoogleSitemapsLayer in utils.registered_layers(),
                         False, "Still registered 'IGoogleSitemapsLayer' "
                         "browser layer")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGoogleSitemapsInstallation))
    suite.addTest(unittest.makeSuite(TestGoogleSitemapsUninstallation))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
#    framework()
