#
# Tests for quintagroup.plonegooglesitemaps upgrading
#

import logging

from quintagroup.plonegooglesitemaps.tests.base import TestCase
import unittest

from StringIO import StringIO

from Products.CMFPlone.utils import _createObjectByType
from Products.GenericSetup.upgrade import _upgrade_registry
from quintagroup.plonegooglesitemaps import config
from quintagroup.plonegooglesitemaps import upgrades as gsm_upgrades
from quintagroup.plonegooglesitemaps import setuphandlers as sh
from quintagroup.canonicalpath.interfaces import ICanonicalPath
from quintagroup.canonicalpath.interfaces import ICanonicalLink


class TestUpgrade(TestCase):

    def afterSetUp(self):
        super(TestUpgrade, self).afterSetUp()
        self.setup = self.portal.portal_setup
        self.profile = "quintagroup.plonegooglesitemaps:default"

    def getUpgradeStep(self, sortkey):
        upgrades = self.setup.listUpgrades(self.profile, show_old=True)
        upgrade_id = upgrades[sortkey - 1]["id"]
        step = _upgrade_registry.getUpgradeStep(self.profile, upgrade_id)
        return step

    def test_upgradeStepsRegistration(self):
        # Test upgrade steps
        upgrades = self.setup.listUpgrades(self.profile, show_old=True)
        self.assertEqual(len(upgrades), 2)
        self.assertEqual(upgrades[0]["title"].endswith("1.0 to 1.1"), True)
        self.assertEqual(upgrades[1]["title"].endswith("1.1 to 1.2"), True)

    def test_upgradeSetupRegistration(self):
        # Test registered upgrade profiles
        pids = [i['id'] for i in self.setup.listProfileInfo()]
        self.assertEqual("quintagroup.plonegooglesitemaps:upgrade_1_0_to_1_1"
                         in pids, True)
        self.assertEqual("quintagroup.plonegooglesitemaps:upgrade_1_1_to_1_2"
                         in pids, True)

    def test_step_1_0_to_1_1(self):
        # Prepare testing data
        catalog = self.portal.portal_catalog
        if "canonical_path" in catalog._catalog.names:
            catalog.delColumn("canonical_path")
        # Upgrade to 1.1 version
        step = self.getUpgradeStep(1)
        if step is not None:
            step.doStep(self.setup)
        # Canonical_path column must be added to portal_catalog
        self.assertEqual("canonical_path" in catalog._catalog.names, True)

    def test_step_1_1_to_1_2(self):
        # Prepare testing data
        catalog = self.portal.portal_catalog
        # Create container folder, update its canonical path
        folder = _createObjectByType('Folder', self.portal, id='test_folder')
        fldr_cpath = "/my_test_home_folder"
        fldr_clink = self.portal.absolute_url() + fldr_cpath
        ICanonicalPath(folder).canonical_path = fldr_cpath
        # Create inner document, update its canonical_path
        doc = _createObjectByType('Document', folder, id='test_doc')
        doc_cpath = "/test_folder/my_test_doc"
        doc_clink = self.portal.absolute_url() + doc_cpath
        ICanonicalPath(doc).canonical_path = doc_cpath
        # Add canonical_path column in catalog
        if not "canonical_path" in catalog._catalog.names:
            catalog.addColumn("canonical_path")
        # Upgrade to 1.2 version
        step = self.getUpgradeStep(2)
        if step is not None:
            step.doStep(self.setup)
        # canonical_link column replace canonical_path
        # one in the portal_catalog
        self.assertEqual("canonical_link" in catalog._catalog.names, True)
        self.assertEqual("canonical_path" in catalog._catalog.names, False)
        # canonical_link property refactored from canonical_path one
        # for inner doc
        self.assertNotEqual(ICanonicalPath(doc).canonical_path, doc_cpath)
        self.assertEqual(ICanonicalLink(doc).canonical_link, doc_clink)
        # canonical_link property refactored from canonical_path one
        # for home folder
        self.assertNotEqual(ICanonicalPath(folder).canonical_path, fldr_cpath)
        self.assertEqual(ICanonicalLink(folder).canonical_link, fldr_clink)

    def testUpgradeCallOnQIReinstall(self):
        # Get upgrade steps
        upgrades = _upgrade_registry.getUpgradeStepsForProfile(self.profile)
        upgrades = dict([(u.sortkey, u) for u in upgrades.values()])
        orig_ver = self.setup.getLastVersionForProfile(self.profile)
        self.setup.setLastVersionForProfile(self.profile, "")
        try:
            # Replace original handlers with patched ones for test calls
            called = []
            upgrades[1].handler = lambda st: called.append("1.0 to 1.1")
            upgrades[2].handler = lambda st: called.append("1.1 to 1.2")
            # Run reinstallation
            qi = self.portal.portal_quickinstaller
            qi.reinstallProducts(products=config.PROJECTNAME)
            # Test upgrades call
            self.assertEqual("1.0 to 1.1" in called, True)
            self.assertEqual("1.1 to 1.2" in called, True)
        finally:
            # Restore original upgrade handlers
            upgrades[1].handler = gsm_upgrades.upgrade_1_0_to_1_1
            upgrades[2].handler = gsm_upgrades.upgrade_1_1_to_1_2
            self.setup.setLastVersionForProfile(self.profile, orig_ver)

try:
    from Products.qPloneGoogleSitemaps.content.sitemap import Sitemap \
        as OldSitemap
except ImportError:
    PRESENT_OLD_PRODUCT = False
else:
    PRESENT_OLD_PRODUCT = True


class TestMigrationFromProduct(TestCase):

    def afterSetUp(self):
        super(TestMigrationFromProduct, self).afterSetUp()
        self.patch_logger()
        self.gs = self.portal.portal_setup
        self.profile = u'profile-quintagroup.plonegooglesitemaps:migrate_qPGSM'
        self.step = "migrate_qPGSM"

    def patch_logger(self):
        logger = logging.Logger("test:GSM", logging.NOTSET)
        self.log = StringIO()
        self.thndlr = logging.StreamHandler(self.log)
        self.thndlr.setLevel(logging.DEBUG)
        self.thndlr.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(self.thndlr)

        self.orig_logger = sh.logger
        sh.logger = logger

    def beforeTearDown(self):
        sh.logger = self.orig_logger

    def chkLog(self, chkstr):
        self.thndlr.flush()
        self.log.seek(0)
        logs = self.log.getvalue().split('\n')
        return chkstr in logs

    def testRemoveOldConfiglet(self):
        chk_str = "Unregistered 'qPloneGoogleSitemaps' "\
                  "configlet from portal_controlpanel tool."
        # 1. No qPloneGoogleSitemaps configlet
        self.gs.runImportStepFromProfile(self.profile, self.step)
        self.assert_(not self.chkLog(chk_str), self.log.getvalue())
        # 2. qPloneGoogleSitemaps configlet in portal
        self.portal.portal_controlpanel.registerConfiglet(
            id="qPloneGoogleSitemaps", name="qPloneGoogleSitemaps",
            action="string:")
        self.gs.runImportStepFromProfile(self.profile, self.step)
        self.assert_(self.chkLog(chk_str), self.log.getvalue())

    def testRemoveOldSkinLayer(self):
        chk_str = "Removed 'qPloneGoogleSitemaps' from 'Plone Default' skin."
        # 1. No qPloneGoogleSitemaps layer in portal_skins
        self.gs.runImportStepFromProfile(self.profile, self.step)
        self.assert_(not self.chkLog(chk_str), self.log.getvalue())
        # 2. qPloneGoogleSitemaps layer in portal_skins
        skins = self.portal.portal_skins
        skinpath = 'qPloneGoogleSitemaps,' + skins.getSkinPath("Plone Default")
        skins._getSelections()["Plone Default"] = skinpath
        self.gs.runImportStepFromProfile(self.profile, self.step)
        self.assert_(self.chkLog(chk_str), self.log.getvalue())

    def testRecriateOldSitemaps(self):
        chk_str = "Successfully replaced '/%s/sitemap.xml' Sitemap" \
                  % self.portal.id
        # 1. No old sitemap present in portal
        self.gs.runImportStepFromProfile(self.profile, self.step)
        self.assert_(not self.chkLog(chk_str), self.log.getvalue())
        # 2. Add old sitemap object in to portal
        self.portal.invokeFactory("Sitemap", 'sitemap.xml')
        self.assert_('sitemap.xml' in self.portal.objectIds(),
                     self.portal.objectIds())
        sm = self.portal['sitemap.xml']
        sm.__class__ = OldSitemap
        self.gs.runImportStepFromProfile(self.profile, self.step)
        self.assert_(self.chkLog(chk_str), self.log.getvalue())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUpgrade))
    if PRESENT_OLD_PRODUCT:
        suite.addTest(unittest.makeSuite(TestMigrationFromProduct))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
