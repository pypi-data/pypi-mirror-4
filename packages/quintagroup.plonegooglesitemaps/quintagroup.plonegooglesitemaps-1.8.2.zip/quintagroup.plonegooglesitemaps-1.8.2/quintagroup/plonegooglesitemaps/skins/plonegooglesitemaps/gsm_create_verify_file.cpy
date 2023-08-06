## Script (Python) "create_verify_file"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Create file for verification
##

from Products.CMFCore.utils import getToolByName
portal = getToolByName(context, 'portal_url').getPortalObject()
sitemap_view = portal.restrictedTraverse("sitemap_settings")
isAdded, res = sitemap_view.uploadVerificationFile(context.REQUEST)
if isAdded:
    state.set(status="success",
              portal_status_message = 'Plone Google Sitemap updated.')
else:
    state.set(status="failure",
              portal_status_message = 'Error on file upload: "%s"' % res)
    #context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')

return state
