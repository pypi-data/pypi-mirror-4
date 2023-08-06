#
# Tests related to general Sitemap type.
#
from quintagroup.plonegooglesitemaps.tests.base import TestCase
import unittest

from types import ListType, TupleType
from zope.component import queryMultiAdapter

from Products.CMFPlone.utils import _createObjectByType
from quintagroup.plonegooglesitemaps.interfaces import IBlackoutFilter


class TestBOFilters(TestCase):

    def testDefaultId(self):
        idfilter = queryMultiAdapter((self.portal, self.app.REQUEST),
                                     IBlackoutFilter, name="id")
        self.assertTrue(idfilter is not None,
                        "Not registered default 'id' IBlackoutFilter")

    def testDefaultPath(self):
        pathfilter = queryMultiAdapter((self.portal, self.app.REQUEST),
                                       IBlackoutFilter, name="path")
        self.assertTrue(pathfilter is not None,
                        "Not registered default 'path' IBlackoutFilter")


class TestFilterMixin(TestCase):

    def afterSetUp(self):
        super(TestFilterMixin, self).afterSetUp()
        self.createTestContent()
        self.sm = _createObjectByType('Sitemap', self.portal,
                                      id='google-sitemaps')
        self.req = self.app.REQUEST
        self.catres = self.portal.portal_catalog(portal_type=["Document", ])
        self.logout()

    def createTestContent(self):
        # Add testing content to portal
        for cont in [self.portal, self.folder]:
            for i in range(1, 4):
                doc = _createObjectByType('Document', cont, id='doc%i' % i)
                doc.edit(text_format='plain', text='hello world %i' % i)
                self.workflow.doActionFor(doc, 'publish')


class TestDefaultFilters(TestFilterMixin):

    def getPreparedLists(self, fname, fargs):
        fengine = queryMultiAdapter((self.sm, self.req), IBlackoutFilter,
                                    name=fname)
        filtered = [f.getPath() for f in fengine.filterOut(self.catres, fargs)]
        catpaths = [c.getPath() for c in self.catres]
        return catpaths, filtered

    def testIdFilter(self):
        catpaths, filtered = self.getPreparedLists("id", "doc1")
        self.assertTrue(type(filtered) in [ListType, TupleType],
                        'Object type, returned by filteredOut method'
                        ' of "id" filter '
                        'not list nor tuple')
        excluded = ["/%s/doc1" % self.portal.absolute_url(1),
                    "/%s/doc1" % self.folder.absolute_url(1)]
        self.assertTrue(
            set(catpaths) - set(filtered) == set(excluded),
            'Wrong filtered-out by "id" filter:\nsrc %s\nres %s\nexcluded %s'
            % (catpaths, filtered, excluded))

    def testAbsolutePathFilter(self):
        catpaths, filtered = self.getPreparedLists("path", "/doc1")
        self.assertTrue(type(filtered) in [ListType, TupleType],
                        'Object type, returned by filteredOut method'
                        ' of "path" filter '
                        'not list nor tuple')
        excluded = ["/%s/doc1" % self.portal.absolute_url(1)]
        self.assertTrue(
            set(catpaths) - set(filtered) == set(excluded),
            'Wrong filtered-out by "path" filter:\nsrc %s\nres %s\nexcluded '
            '%s' % (catpaths, filtered, excluded))

    def testRelativePathFilter(self):
        self.sm = _createObjectByType('Sitemap', self.folder,
                                      id='google-sitemaps')
        catpaths, filtered = self.getPreparedLists("path", "./doc1")
        self.assertTrue(type(filtered) in [ListType, TupleType],
                        'Object type, returned by filteredOut method'
                        ' of "path" utility '
                        'not list nor tuple')
        excluded = ["/%s/doc1" % self.folder.absolute_url(1)]
        self.assertTrue(
            set(catpaths) - set(filtered) == set(excluded),
            'Wrong filtered-out by "path" filter:\nsrc %s\nres %s\nexcluded '
            '%s' % (catpaths, filtered, excluded))


class TestBlacklistFormProcessing(TestFilterMixin):

    def afterSetUp(self):
        super(TestBlacklistFormProcessing, self).afterSetUp()
        self.loginAsPortalOwner()
        self.smview = queryMultiAdapter((self.sm, self.app.REQUEST),
                                        name="sitemap.xml")

    def getPreparedLists(self, bl, fargs):
        self.sm.edit(blackout_list=[bl, ])
        filtered = [f['url'] for f in self.smview.results()]
        catpaths = [c.getURL() for c in self.catres]
        return catpaths, filtered

    def testGetNamedFilterUtility(self):
        catpaths, filtered = self.getPreparedLists("path:/doc1", "/plone/doc1")
        excluded = ["%s/doc1" % self.portal.absolute_url(),
                    "%s/front-page" % self.portal.absolute_url()]
        self.assertTrue(set(catpaths) - set(filtered) == set(excluded),
                        'Wrong filtered-out by'
                        ' "id" filter:\nsrc %s\nres %s\nexcluded %s'
                        % (catpaths, filtered, excluded))

    def testDefaultFilterUtility(self):
        catpaths, filtered = self.getPreparedLists("id:doc1", "doc1")
        excluded = ["%s/doc1" % self.portal.absolute_url(),
                    "%s/front-page" % self.portal.absolute_url(),
                    "%s/doc1" % self.folder.absolute_url()]
        self.assertTrue(set(catpaths) - set(filtered) == set(excluded),
                        'Wrong filtered-out by "id" '
                        'filter:\nsrc %s\nres %s\nexcluded %s'
                        % (catpaths, filtered, excluded))
        # Now check is output of unnamed filter samed to named one.
        self.sm.edit(blackout_list=["doc1", ])
        filtered_dflt = [f['url'] for f in self.smview.results()]
        map(lambda l: l.sort(), (filtered, filtered_dflt))
        self.assertTrue(filtered == filtered_dflt,
                        'Output of named "id" filter '
                        'is not same to unnamed one:\n'
                        'id-named: %s\nunnamed: %s'
                        % (filtered, filtered_dflt))

    # def testGetCorrectFilterName(self):
    #     from zope import component
    #     call_names = []
    #     origQMA = component._api.queryMultiAdapter
    #     def patchQMA(objects, interface=Interface, name=u'', context=None):
    #         call_names.append(name)
    #         origQMA(objects, interface=interface, name=name, context=context)
    #     component.queryMutliAdapter = patchQMA
    #     self.sm.edit(blackout_list="FooFilterName:arg1:arg2:doc1")
    #     self.smview.results()
    #     self.assertTrue("FooFilterName" in call_names, "Wrong filter " \
    #         "name parsing - no FooFilterName in %s" % call_names)
    #     component._api.queryMutliAdapter = origQMA


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBOFilters))
    suite.addTest(unittest.makeSuite(TestDefaultFilters))
    suite.addTest(unittest.makeSuite(TestBlacklistFormProcessing))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
#    framework()
