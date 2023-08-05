from zope.interface import implements, Interface, Attribute
from zope.component import queryMultiAdapter

from Acquisition import aq_inner, aq_parent
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

#from quintagroup.plonegooglesitemaps \
#    import qPloneGoogleSitemapsMessageFactory as _
from quintagroup.plonegooglesitemaps.interfaces import IBlackoutFilter
from quintagroup.plonegooglesitemaps.browser.utils import additionalURLs, \
    applyOperations


class ISitemapView(Interface):
    """
    Sitemap view interface
    """

    def results():
        """ Return list of dictionary objects
            which confirm Sitemap conditions
        """

    def getAdditionalURLs():
        """ Return additional URL list
        """

    def updateRequest():
        """ Add compression header to RESPONSE
            if allowed
        """

    numEntries = Attribute("Return number of entries")


class CommonSitemapView(BrowserView):
    """
    Sitemap browser view
    """
    implements(ISitemapView)

    # key, function map for extend return results
    # with mapping data
    additional_maps = ()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def search_path(self):
        return '/'.join(aq_parent(aq_inner(self.context)).getPhysicalPath())

    def getFilteredObjects(self):
        """ Return brains
        """
        return []

    def results(self):
        """ Prepare mapping for template
        """
        result = []
        objects = self.getFilteredObjects()
        reg_exps = self.context.getReg_exp()

        brain_url_map = applyOperations(self.getBOFiltered(objects), reg_exps)
        # Prepare dictionary for view
        for url, b in brain_url_map.items():
            res_map = {'url': url, }
            [res_map.update({k: f(b)}) for k, f in self.additional_maps]
            result.append(res_map)
        self.num_entries = len(result)
        return result

    def getBOFiltered(self, objects):
        """Return black-out filtered objects
          Every record in blackout_list filter should follow the spec:
            [<filter name>:]<filter arguments>
          For example:
          1|  index.html
          2|  id:index.html
          3|  path:/folder_1_level/obj_in_folder
          4|  path:./folder_near_sitemap/obj_in_folder
          5|  foo_filter:arg-1, arg-2

          1->used default "id" filter - remove "index.html" objects;
          2->explicit "id" filter - remove "index.html" objects;
          3->"path" filter - remove /folder_1_level/obj_in_folder object,
              path from the root of the plone site;
          4->same to 3), but path get from the folder, where sitemap is
             located;
          5->filter name is "foo_filter" (must be registered IBlackoutFilter,
             named "foo_filter"), which get filter arguments: arg-1, arg-2

          Detailed explanation look in filters.txt doctest.
        """
        blackout_list = self.context.getBlackout_list()
        for frec in blackout_list:
            fspec = frec.split(":", 1)
            fargs = fspec.pop()
            fname = fspec and fspec.pop() or "id"
            fengine = queryMultiAdapter((self.context, self.request),
                                        interface=IBlackoutFilter,
                                        name=fname)
            if fengine:
                objects = list(fengine.filterOut(objects, fargs))
        return objects

    def updateRequest(self):
        self.request.RESPONSE.setHeader('Content-Type', 'text/xml')
        try:
            compression = self.context.enableHTTPCompression()
            if compression:
                compression(request=self.request)
        except:
            pass

    def getAdditionalURLs(self):
        return additionalURLs(self.context)

    @property
    def numEntries(self):
        return len(self.results()) + len(self.getAdditionalURLs())
