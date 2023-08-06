import logging
from zope.component import queryMultiAdapter

from quintagroup.canonicalpath.upgrades import CanonicalConvertor

logger = logging.getLogger('quintagroup.plonegooglesitemaps')

convertor = None


def migrateCanonical(plone_tools):
    """ Rename qSEO_canonical property into PROPERTY_LINK
        for all portal objects, which use SEO
    """
    global convertor
    types = plone_tools.types()
    purl = plone_tools.url()
    portal = purl.getPortalObject()
    allCTTypes = types.listContentTypes()
    obj_metatypes = [m.content_meta_type for m in types.objectValues()
                     if m.getId() in allCTTypes]
    convertor = CanonicalConvertor(portal_url=purl())
    portal.ZopeFindAndApply(portal,
                            obj_metatypes=','.join(obj_metatypes),
                            apply_func=renameProperty,
                            search_sub=1,)
    print convertor.getLogs()


def renameProperty(obj, path):
    """ Migrate canonical_path property into canonical_link
        for obj, which use SEO
    """
    if convertor is not None:
        convertor.convertIPathToLink(obj)


def upgrade_1_0_to_1_1(setuptool):
    """ Upgrade quintagroup.plonegooglesitemaps from version 1.0 to 1.1.
    """
    profile_name = 'profile-quintagroup.plonegooglesitemaps:upgrade_1_0_to_1_1'
    setuptool.runAllImportStepsFromProfile(profile_name)


def upgrade_1_1_to_1_2(setuptool):
    """ Upgrade quintagroup.plonegooglesitemaps from version 1.1 to 1.2.
    """
    plone_tools = queryMultiAdapter((setuptool, setuptool.REQUEST),
                                    name="plone_tools")
    migrateCanonical(plone_tools)
    profile_name = 'profile-quintagroup.plonegooglesitemaps:upgrade_1_1_to_1_2'
    setuptool.runAllImportStepsFromProfile(profile_name)
