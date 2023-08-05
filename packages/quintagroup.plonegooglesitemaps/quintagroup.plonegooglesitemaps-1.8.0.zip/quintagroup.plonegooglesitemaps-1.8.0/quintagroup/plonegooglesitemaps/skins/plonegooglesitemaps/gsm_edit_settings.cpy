## Script (Python) "gsm_edit_settings"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##bind state=state
##parameters=
##title=Configure Plone Google Sitemap
##

from Products.CMFCore.utils import getToolByName
from quintagroup.plonegooglesitemaps.utils import ping_google

portal_url = getToolByName(context,'portal_url')
portalURL = portal_url()
portal = portal_url.getPortalObject()
req = context.REQUEST
message = ""

def addSMByType(parent, sm_type, sm_id):
    new_id = portal.invokeFactory(id=sm_id, type_name="Sitemap", sitemapType=sm_type)
    sm = getattr(portal, new_id)
    if sm:
        sm.markCreationFlag()
        return new_id
    return None

if req.get('form.button.AddContent', False):
    new_id = addSMByType(portal, 'content', 'sitemap.xml')
    if new_id:
        return req.RESPONSE.redirect("%s/%s/edit" % (portalURL, new_id))
    else:
        message = "Can't create content sitemap"
elif req.get('form.button.AddMobile', False):
    new_id = addSMByType(portal, 'mobile', 'mobile-sitemap.xml')
    if new_id:
        return req.RESPONSE.redirect("%s/%s/edit" % (portalURL, new_id))
    else:
        message = "Can't create mobile sitemap"
elif req.get('form.button.AddNews', False):
    new_id = addSMByType(portal, 'news', 'news-sitemap.xml')
    if new_id:
        return req.RESPONSE.redirect("%s/%s/edit" % (portalURL, new_id))
    else:
        message = "Can't create news sitemap"
else:
    smselected = req.get('smselected', [])

    if req.get('form.button.Delete', False):
        portal.manage_delObjects(ids=smselected[:])
        message = "Succesfully deleted: %s" % smselected

    elif req.get('form.button.Ping', False):
        pinged = []
        message = "Google pinged. It will review your sitemap as soon as it will be able to. Processed: %s"
        for sm_id in smselected:
            try:
                ping_google(portalURL, sm_id)
            except:
                message = "Cannot contact Google. Try again in a while. But pinged for: %s"
                break
            else:
                pinged.append(sm_id)
        message = message % pinged

return state.set(next_action='traverse_to:string:prefs_gsm_settings',
                 portal_status_message = message)
