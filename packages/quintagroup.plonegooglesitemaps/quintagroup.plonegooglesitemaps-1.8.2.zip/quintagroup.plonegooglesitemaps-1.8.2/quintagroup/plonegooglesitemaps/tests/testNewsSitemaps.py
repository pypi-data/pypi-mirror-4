from quintagroup.plonegooglesitemaps.tests.base \
    import FunctionalTestCase, TestCase, IGoogleSitemapsLayer
from quintagroup.plonegooglesitemaps.tests.XMLParser import parse
from Products.PloneTestCase.setup import portal_owner, default_password
from zope.interface import alsoProvides
import unittest

from DateTime import DateTime
from Missing import MV

from zope.publisher.browser import TestRequest
from zope.component import queryMultiAdapter
from zope.component import adapts, provideAdapter
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getSiteManager, getGlobalSiteManager
from zope.interface import implements, Interface, classImplements
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender

from Products.CMFPlone.utils import _createObjectByType
from Products.Archetypes.public import StringField
from Products.ATContentTypes.content.newsitem import ATNewsItem


class TestNewsSitemapsXML(FunctionalTestCase):

    def afterSetUp(self):
        super(TestNewsSitemapsXML, self).afterSetUp()
        # Create news sitemaps
        _createObjectByType("Sitemap", self.portal, id="news-sitemaps",
                            sitemapType="news", portalTypes=("News Item",))
        self.portal["news-sitemaps"].at_post_create_script()
        # Add testing news item to portal
        self.pubdate = (DateTime() + 1).strftime("%Y-%m-%d")
        self.my_news = _createObjectByType('News Item', self.portal,
                                           id='my_news')
        self.my_news.edit(text="Test news item",
                          title="First news (test)",
                          language="ua",
                          effectiveDate=self.pubdate,
                          gsm_access="Registration",
                          gsm_genres=("PressRelease",),
                          gsm_stock="NASDAQ:AMAT, BOM:500325")
        self.workflow.doActionFor(self.my_news, "publish")
        self.reParse()

    def reParse(self):
        # Parse news sitemap
        self.sitemap = self.publish("/" + self.portal.absolute_url(1) +
                                    "/news-sitemaps",
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
        self.assertEqual(urlset.get("xmlns:n", ""),
                         "http://www.google.com/schemas/sitemap-news/0.9")

    def test_url(self):
        self.assert_("url" in self.start.keys())

    def test_loc(self):
        self.assert_("loc" in self.start.keys())
        self.assert_(self.portal.absolute_url() + "/my_news" in self.data)

    def test_nnews(self):
        self.assert_("n:news" in self.start.keys())

    def test_npublication(self):
        self.assert_("n:publication" in self.start.keys())
        self.assert_("n:name" in self.start.keys())
        self.assert_("First news" in self.data, "No 'First news' in data")
        self.assert_("n:language" in self.start.keys())
        self.assert_("ua" in self.data, "No 'ua' in data")

    def test_npublication_date(self):
        self.assert_("n:publication_date" in self.start.keys())
        self.assert_(self.pubdate in self.data, "No %s in data" % self.pubdate)

    def test_ntitle(self):
        self.assert_("n:title" in self.start.keys())
        self.assert_("First news (test)" in self.data,
                     "No 'First news (test)' in data")

    def test_naccess(self):
        # Test when access present
        self.assert_("n:access" in self.start.keys())
        self.assert_("Registration" in self.data, "No 'Registration' in data")

    def test_ngenres(self):
        # Test when genres present
        self.assert_("n:genres" in self.start.keys())
        self.assert_("PressRelease" in self.data, "No 'PressRelease' in data")

    def test_ngenresMultiple(self):
        # Test multiple genres
        self.my_news.edit(gsm_genres=("PressRelease", "Blog"))
        self.my_news.reindexObject()
        self.reParse()
        self.assert_("n:genres" in self.start.keys())
        self.assert_("PressRelease, Blog" in self.data,
                     "No 'PressRelease, Blog' in data")

    def test_ngenresEmpty(self):
        # No genres should present if it's not updated
        self.my_news.edit(gsm_genres=[])
        self.my_news.reindexObject()
        self.reParse()
        self.assertNotEqual("n:genres" in self.start.keys(), True)

    def test_ngenresForNotExtended(self):
        # No genres should present for not extended content type
        my_doc = _createObjectByType('Document', self.portal, id='my_doc')
        my_doc.edit(text="Test document")
        self.workflow.doActionFor(my_doc, "publish")
        self.portal["news-sitemaps"].edit(portalTypes=("Document",))
        self.reParse()
        self.assertNotEqual("n:genres" in self.start.keys(), True)

    def test_nstock_tickers(self):
        # Test n:stock_tickers
        self.assert_("n:stock_tickers" in self.start.keys())
        self.assert_("NASDAQ:AMAT, BOM:500325" in self.data,
                     "No 'NASDAQ:AMAT, BOM:500325' in data")


class TestNewsSitemapsXMLDefaultObject(FunctionalTestCase):

    def afterSetUp(self):
        super(TestNewsSitemapsXMLDefaultObject, self).afterSetUp()
        # Create news sitemaps
        _createObjectByType("Sitemap", self.portal, id="news-sitemaps",
                            sitemapType="news", portalTypes=("News Item",))
        self.portal["news-sitemaps"].at_post_create_script()
        # Add minimal testing news item to portal
        self.pubdate = (DateTime() + 1).strftime("%Y-%m-%d")
        self.my_news = _createObjectByType('News Item', self.portal,
                                           id='my_news')
        self.my_news.edit(effectiveDate=self.pubdate)
        self.workflow.doActionFor(self.my_news, "publish")
        self.reParse()

    def reParse(self):
        # Parse news sitemap
        self.sitemap = self.publish("/" + self.portal.absolute_url(1) +
                                    "/news-sitemaps",
                                    "%s:%s" % (portal_owner, default_password)
                                    ).getBody()
        parsed_sitemap = parse(self.sitemap)
        self.start = parsed_sitemap["start"]
        self.data = parsed_sitemap["data"]

    def test_nnews(self):
        self.assert_("n:news" in self.start.keys())

    def test_npublication(self):
        self.assert_("n:publication" in self.start.keys())
        self.assert_("n:name" in self.start.keys())
        self.assert_("my_news" in self.data, "No 'First news' in data")
        self.assert_("n:language" in self.start.keys())
        self.assert_("en" in self.data, "No 'en' in data")

    def test_npublication_date(self):
        self.assert_("n:publication_date" in self.start.keys())
        self.assert_(self.pubdate in self.data, "No %s in data" % self.pubdate)

    def test_ntitle(self):
        self.assert_("n:title" in self.start.keys())
        self.assert_("my_news" in self.data, "No 'First news (test)' in data")

    def test_no_naccess(self):
        self.assert_("n:access" not in self.start.keys())

    def test_no_ngenres(self):
        self.assert_("n:genres" not in self.start.keys())

    def test_no_keywords(self):
        self.assert_("n:keywords" not in self.start.keys())

    def test_no_stock_tickers(self):
        self.assert_("n:stock_tickers" not in self.start.keys())


class TestSchemaExtending(TestCase):

    def afterSetUp(self):
        super(TestSchemaExtending, self).afterSetUp()
        self.my_doc = _createObjectByType('Document', self.portal, id='my_doc')
        self.my_news = _createObjectByType('News Item', self.portal,
                                           id='my_news')

    def testExtendNewsItemByDefault(self):
        # Neither of object has extended fields
        self.assertNotEqual(self.my_news.getField("gsm_access"), None)
        self.assertNotEqual(self.my_news.getField("gsm_genres"), None)
        self.assertNotEqual(self.my_news.getField("gsm_stock"), None)
        self.assertEqual(self.my_doc.getField("gsm_access"), None)
        self.assertEqual(self.my_doc.getField("gsm_genres"), None)
        self.assertEqual(self.my_doc.getField("gsm_stock"), None)

    def testRegistrationOnLocalSM(self):
        """SchemaExtender adapters must be registered
           in Local SiteManager only.
        """
        localsm = getSiteManager(self.portal)
        globalsm = getGlobalSiteManager()
        # Now register SchemaExtender adapter and
        # check if it present in Local SiteManger only
        adapter = "quintagroup.plonegooglesitemaps.newssitemapextender"
        self.assertNotEqual(localsm, globalsm)
        self.assertNotEqual(localsm.queryAdapter(
                            self.my_news, ISchemaExtender,
                            name=adapter),
                            None)
        self.assertEqual(globalsm.queryAdapter(
                         self.my_news, ISchemaExtender,
                         name=adapter),
                         None)


##
## Mock objects for TestNotOverrideExistingSchemaExtender
## Test Case
##

class ITestTaggable(Interface):
    """Taggable content

"""


class ExtendableStringField(ExtensionField, StringField):
    """An extendable string field."""


class TestExtender(object):
    adapts(ITestTaggable)
    implements(ISchemaExtender)

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return [ExtendableStringField("testField",), ]

from quintagroup.plonegooglesitemaps.interfaces import INewsSitemapProvider


class TestNotOverrideExistingSchemaExtender(TestCase):
    """ Test if another schemaextender has been defined for the
        IATNewsItem take in account by the system.
    """
    def prepareContent(self):

        classImplements(ATNewsItem, ITestTaggable)
        provideAdapter(TestExtender,
                       name=u"archetypes.schemaextender.test.adapter")

        self.portal.invokeFactory('News Item', 'taggable-news')
        self.taggable_news = getattr(self.portal, 'taggable-news')

    def testCorrectSchemaExtending(self):
        self.prepareContent()
        self.assert_(ITestTaggable.providedBy(self.taggable_news))
        self.assert_(INewsSitemapProvider.providedBy(self.taggable_news))
        schema = self.taggable_news.Schema().keys()
        self.assert_("gsm_access" in schema, "no 'gsm_access' in schema: %s"
                     % schema)
        self.assert_("testField" in schema, "no 'testField' in schema: %s"
                     % schema)


classImplements(TestRequest, IAttributeAnnotatable)


class TestAdditionalMaps(TestCase):
    """Test bug in processing Missing value in functions,
       defined in additional_maps property.
    """
    mv_keys = ['Date', 'Subject', 'getId', 'Language',
               'gsm_access', 'gsm_genres', 'gsm_stock']

    def afterSetUp(self):
        super(TestAdditionalMaps, self).afterSetUp()
        # Create news sitemaps
        _createObjectByType("Sitemap", self.portal, id="news-sitemaps",
                            sitemapType="news")
        context = self.portal['news-sitemaps']
        request = TestRequest()
        alsoProvides(request, IGoogleSitemapsLayer)
        self.nsmv = queryMultiAdapter((context, request),
                                      name="news-sitemap.xml")

        self.brain = self.portal.portal_catalog(portal_type="Document")[0]
        for k in self.mv_keys:
            self.brain[k] = MV

    def testAdditionalMaps(self):
        for n, func in self.nsmv.additional_maps:
            try:
                func(self.brain)
            except Exception, e:
                self.fail("Wrong processing 'Missing' value for '%s': %s"
                          % (n, str(e)))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNewsSitemapsXML))
    suite.addTest(unittest.makeSuite(TestNewsSitemapsXMLDefaultObject))
    suite.addTest(unittest.makeSuite(TestSchemaExtending))
    suite.addTest(unittest.makeSuite(TestNotOverrideExistingSchemaExtender))
    suite.addTest(unittest.makeSuite(TestAdditionalMaps))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
#    framework()
