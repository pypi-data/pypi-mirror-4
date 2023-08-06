import logging
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.upgrade import _upgrade_registry

logger = logging.getLogger("quintagroup.plonegooglesitemaps")
PROFILE = "profile-quintagroup.plonegooglesitemaps:default"
UNINSTALL = "profile-quintagroup.plonegooglesitemaps:uninstall"


def install(self, reinstall=False):
    """ Install skin with GenericSetup install profile
    """
    ps = getToolByName(self, 'portal_setup')
    mtool = getToolByName(self, 'portal_migration')
    plone_version = mtool.getFileSystemVersion()
    isPlone3 = plone_version.startswith('3')
    isPlone4 = plone_version.startswith('4')

    if reinstall and (isPlone3 or isPlone4):
        step = None
        profile_id = 'quintagroup.plonegooglesitemaps:default'
        steps_to_run = [s['id'] for s in
                        ps.listUpgrades(profile_id, show_old=False)]
        for step_id in steps_to_run:
            step = _upgrade_registry.getUpgradeStep(profile_id, step_id)
            step.doStep(ps)
            msg = "Ran upgrade step %s for profile %s" \
                  % (step.title, profile_id)
            logger.log(logging.INFO, msg)
        # We update the profile version to the last one we have reached
        # with running an upgrade step.
        if step and step.dest is not None and step.checker is None:
            ps.setLastVersionForProfile(profile_id, step.dest)
        return "Ran all reinstall steps."

    if (isPlone3 or isPlone4):
        # if this is plone 3.x
        (ps.aq_base).__of__(self).runAllImportStepsFromProfile(PROFILE)
    else:
        active_context_id = ps.getImportContextID()
        ps.setImportContext(PROFILE)
        ps.runAllImportSteps()
        ps.setImportContext(active_context_id)


def uninstall(portal, reinstall=False):
    """ Uninstall this product.

        This external method is need, because portal_quickinstaller doens't
        know what GenericProfile profile to apply when uninstalling a product.
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    if reinstall:
        return "Ran all reinstall steps."
    else:
        setup_tool.runAllImportStepsFromProfile(UNINSTALL)
        return "Ran all uninstall steps."
