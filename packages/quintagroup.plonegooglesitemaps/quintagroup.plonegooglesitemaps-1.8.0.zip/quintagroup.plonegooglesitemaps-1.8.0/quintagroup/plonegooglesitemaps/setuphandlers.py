import logging
from zope.component import getSiteManager
from zope.component import getGlobalSiteManager

from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName

from config import SUPPORT_BLAYER
from quintagroup.plonegooglesitemaps.content.newsextender import NewsExtender

logger = logging.getLogger('quintagroup.plonegooglesitemaps')


def unregisterSchemaExtenderAdapters(site):
    """ Unregister news schema extender adapters
        from local component registry.
    """
    lsm = getSiteManager(site)
    gsm = getGlobalSiteManager()
    if lsm == gsm:
        logger.warning("Not found local component registry")
        return

    unregistered = []
    registrations = tuple(lsm.registeredAdapters())
    for registration in registrations:
        factory = registration.factory
        if factory == NewsExtender:
            required = registration.required
            provided = registration.provided
            name = registration.name
            lsm.unregisterAdapter(factory=factory,
                                  required=required,
                                  provided=provided,
                                  name=name)
            unregistered.append(str(required))
    logger.info("Unregistered news schema extender adapters for: %s"
                % unregistered)


def removeConfiglet(site):
    """ Remove configlet.
    """
    conf_id = 'GoogleSitemaps'
    controlpanel_tool = getToolByName(site, 'portal_controlpanel')
    if controlpanel_tool:
        controlpanel_tool.unregisterConfiglet(conf_id)
        logger.log(logging.INFO, "Unregistered \"%s\" configlet." % conf_id)


def removeBrowserLayer(site):
    """ Remove browser layer.
    """
    if not SUPPORT_BLAYER:
        return

    from plone.browserlayer.utils import unregister_layer
    from plone.browserlayer.interfaces import ILocalBrowserLayerType

    name = "quintagroup.plonegooglesitemaps"
    site = getSiteManager(site)
    registeredLayers = [r.name for r in site.registeredUtilities()
                        if r.provided == ILocalBrowserLayerType]
    if name in registeredLayers:
        unregister_layer(name, site_manager=site)
        logger.log(logging.INFO, "Unregistered \"%s\" browser layer." % name)


def uninstall(context):
    """ Do customized uninstallation.
    """
    if context.readDataFile('gsm_uninstall.txt') is None:
        return
    site = context.getSite()
    unregisterSchemaExtenderAdapters(site)
    removeConfiglet(site)
    removeBrowserLayer(site)


def cleanup(site):
    """Clean-up qPloneGoogleSitemaps artefacts."""
    old_product = "qPloneGoogleSitemaps"
    # Get plone tools
    getToolByName(site, 'portal_properties')
    skins = getToolByName(site, 'portal_skins')
    controlpanel = getToolByName(site, 'portal_controlpanel')
    # Remove old configlet from controlpanel
    configlet_ids = [ai['id'] for ai in controlpanel.listActionInfos()]
    if old_product in configlet_ids:
        controlpanel.unregisterConfiglet(old_product)
        logger.info("Unregistered '%s' configlet from "
                    "portal_controlpanel tool." % old_product)
    # Remove qPloneGoogleSitemaps skin layer
    for skinName in skins.getSkinSelections():
        skin_paths = skins.getSkinPath(skinName).split(',')
        paths = [l.strip() for l in skin_paths if not l == old_product]
        if len(paths) < len(skin_paths):
            logger.info("Removed '%s' from '%s' skin."
                        % (old_product, skinName))
        skins.addSkinSelection(skinName, ','.join(paths))


def recriateSitemaps(smaps):
    msg = "Recriation Sitemaps: "
    if smaps:
        logger.info(msg + "Process %s sitemaps." % (
                    [sm.getPath() for sm in smaps]))
        fields = ['id', 'sitemapType', 'portalTypes', 'states',
                  'blackout_list', 'reg_exp', 'urls', 'pingTransitions']
        for smb in smaps:
            # get sitemap properties
            sm_path = smb.getPath()
            sm = smb.getObject()
            container = aq_parent(sm)
            data = {}
            for fn in fields:
                data[fn] = sm.getField(fn).getAccessor(sm)()
            # Replace old GoogleSitemap by new one with
            # previous properties
            container.manage_delObjects(data['id'])
            container.invokeFactory("Sitemap", id=data['id'])
            new_sm = getattr(container, data['id'])
            new_sm.update(**data)
            new_sm.at_post_create_script()
            logger.info("Successfully replaced '%s' Sitemap" % sm_path)


def getOldGSitemaps(site):
    catalog = getToolByName(site, 'portal_catalog')
    smaps = catalog(portal_type="Sitemap")
    old_smb = [smb for smb in smaps
               if 'qPloneGoogleSitemaps' in str(smb.getObject().__class__)]
    return old_smb


def migrate_qPGSM(context):
    """ Clean-up qPloneGoogleSitemaps product artefacts and
        recriate sitemaps from quintagroup.plonegooglesitemaps
        package version 1.0.
    """
    if context.readDataFile('gsm_migration.txt') is None:
        return

    site = context.getSite()
    cleanup(site)
    old_gsmaps = getOldGSitemaps(site)
    if old_gsmaps:
        recriateSitemaps(old_gsmaps)
        logger.info("Successfully migrated old GoogleSitemaps.")
    else:
        logger.info("No old GoogleSitemaps found.")
