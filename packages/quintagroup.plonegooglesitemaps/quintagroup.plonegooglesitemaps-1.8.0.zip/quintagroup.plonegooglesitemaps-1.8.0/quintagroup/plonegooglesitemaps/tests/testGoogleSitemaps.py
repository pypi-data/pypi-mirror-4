#
# Tests for quintagroup.plonegooglesitemaps
#

from quintagroup.plonegooglesitemaps.tests.base import FunctionalTestCase
from quintagroup.plonegooglesitemaps.tests.XMLParser import parse
from StringIO import StringIO
from urllib import urlencode
import re
import unittest

from cgi import FieldStorage
from tempfile import NamedTemporaryFile

from OFS.Image import cookId
from Products.CMFPlone.utils import _createObjectByType
from ZPublisher.HTTPRequest import FileUpload


def prepareUploadFile(prefix=""):
    """ Helper function for prerare file to uploading """
    fp = NamedTemporaryFile(mode='w+', prefix=prefix)
    fp.write("google-site-verification: " + fp.name)
    fp.seek(0, 2)
    fsize = fp.tell()
    fp.seek(0)

    env = {'REQUEST_METHOD': 'PUT'}
    headers = {'content-type': 'text/plain',
               'content-length': fsize,
               'content-disposition': 'attachment; filename=%s' % fp.name}
    fs = FieldStorage(fp=fp, environ=env, headers=headers)
    return FileUpload(fs), fp


class TestGoogleSitemaps(FunctionalTestCase):

    def afterSetUp(self):
        super(TestGoogleSitemaps, self).afterSetUp()

        _createObjectByType('Sitemap', self.portal, id='google-sitemaps')
        self.sitemapUrl = '/' + self.portal.absolute_url(1) + \
                          '/google-sitemaps'
        gsm_properties = 'googlesitemap_properties'
        self.gsm_props = self.portal.portal_properties[gsm_properties]

        # Add testing document to portal
        self.my_doc = _createObjectByType('Document', self.portal, id='my_doc')
        self.my_doc.edit(text_format='plain', text='hello world')

    def testSitemap(self):
        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        parsed_sitemap = parse(sitemap)
        start = parsed_sitemap['start']
        data = parsed_sitemap['data']
        self.assert_('urlset' in start.keys())
        self.assertFalse(self.my_doc.absolute_url(0) in data,
                         'Wrong content present in the sitemap')

        self.workflow.doActionFor(self.my_doc, 'publish')

        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        parsed_sitemap = parse(sitemap)
        start = parsed_sitemap['start']
        data = parsed_sitemap['data']
        self.assertEqual(len(start.keys()), 4)
        self.assert_('urlset' in start.keys())
        self.assert_('url' in start.keys())
        self.assert_('loc' in start.keys())
        self.assert_('lastmod' in start.keys())

        self.assertTrue(self.my_doc.absolute_url(0) in data, 'Incorect url')

    def testVerificationFileCreation(self):
        fp, fname = None, None
        try:
            fupload, fp = prepareUploadFile()
            fname, ftitle = cookId('', '', fupload)
            self.portal.REQUEST.form['verification_file'] = fupload
            self.portal.gsm_create_verify_file()
        finally:
            if fp:
                fp.close()
        vf_created = hasattr(self.portal, fname)
        self.assert_(vf_created, 'Verification file not created')

    def testVerificationForm(self):
        verifyConfigUrl = '/' + self.portal.absolute_url(1) + \
                          '/prefs_gsm_verification'
        verif_config = self.publish(verifyConfigUrl, self.auth).getBody()
        rexp_input_acitve = re.compile('<input\s+name="verification_file"'
                                       '\s+([^>]*)>', re.I | re.S)
        rexp_button_acitve = re.compile(
            '<input\s+name="form.button.CreateFile"\s+([^>]*)>', re.I | re.S)
        rexp_delete_button = re.compile(
            '<input\s+name="form.button.DeleteFile"\s+[^>]*>', re.I | re.S)

        input_acitve = rexp_input_acitve.search(verif_config)
        button_acitve = rexp_button_acitve.search(verif_config)
        delete_button = rexp_delete_button.match(verif_config)

        self.assert_(input_acitve and not 'disabled' in input_acitve.groups(1))
        self.assert_(button_acitve and not 'disabled' in
                     button_acitve.groups(1))
        self.assert_(not delete_button)

        fp, fname = None, None
        try:
            fupload, fp = prepareUploadFile()
            fname, ftitle = cookId('', '', fupload)
            self.portal.REQUEST.form['verification_file'] = fupload
            self.portal.gsm_create_verify_file()
        finally:
            if fp:
                fp.close()

        input_acitve = rexp_input_acitve.search(verif_config)
        button_acitve = rexp_button_acitve.search(verif_config)
        delete_button = rexp_delete_button.match(verif_config)

        verif_config = self.publish(verifyConfigUrl, self.auth).getBody()
        self.assert_(input_acitve and not 'disabled' in input_acitve.groups(1))
        self.assert_(not delete_button)

    def testMultiplyVerificationFiles(self):
        verifyConfigUrl = '/' + self.portal.absolute_url(1) + \
                          '/prefs_gsm_verification'
        fnames = []
        for i in [1, 2]:
            fp, fname, response = None, None, None
            try:
                fupload, fp = prepareUploadFile(prefix=str(i))
                fname, ftitle = cookId('', '', fupload)
                form = {'form.button.CreateFile': 'Create verification file',
                        'form.submitted': 1}
                extra_update = {'verification_file': fupload}
                response = self.publish(verifyConfigUrl, request_method='POST',
                                        stdin=StringIO(urlencode(form)),
                                        basic=self.auth, extra=extra_update)
            finally:
                if fp:
                    fp.close()

            self.assertEqual(response.getStatus(), 200)
            self.assert_(fname in
                         self.gsm_props.getProperty('verification_filenames',
                                                    []),
                         self.gsm_props.getProperty('verification_filenames',
                                                    []))
            fnames.append(fname)

        self.assertEqual(len([1 for vf in fnames
                         if
                         vf
                         in
                         self.gsm_props.getProperty('verification_filenames',
                                                    [])]), 2,
                         self.gsm_props.getProperty('verification_filenames',
                                                    []))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGoogleSitemaps))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
#    framework()
