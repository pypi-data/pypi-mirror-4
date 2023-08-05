import unittest
import doctest

from base import FunctionalTestCase
from Testing import ZopeTestCase as ztc
from Products.CMFPlone.utils import _createObjectByType


class DocTestCase(FunctionalTestCase):

    def afterSetUp(self):
        super(DocTestCase, self).afterSetUp()
        #self.createTestContent()

    def addDocument(self, cont, id, text):
        doc = _createObjectByType('Document', cont, id=id)
        doc.edit(text_format='plain', text=text)
        self.workflow.doActionFor(doc, 'publish')
        #return doc


def test_suite():
    return unittest.TestSuite([

        # Demonstrate the main content types
        ztc.FunctionalDocFileSuite(
            'filters.txt', package='quintagroup.plonegooglesitemaps',
            test_class=DocTestCase, globs=globals(),
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        # | doctest.REPORT_ONLY_FIRST_FAILURE |
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
