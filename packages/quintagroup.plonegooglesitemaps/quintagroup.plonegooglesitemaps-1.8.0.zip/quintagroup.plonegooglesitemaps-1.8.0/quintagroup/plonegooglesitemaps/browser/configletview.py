from zope.component import queryMultiAdapter
from zope.interface import implements, Interface, Attribute

from OFS.Image import cookId
from OFS.ObjectManager import BadRequestException
from Products.Five import BrowserView

import urlparse


def splitNum(num):
    res = []
    prefn = 3
    for c in str(num)[::-1]:
        res.insert(0, c)
        if not len(res) % prefn:
            res.insert(0, ',')
            prefn += 4
    return "".join(res[0] == ',' and res[1:] or res)


class IConfigletSettingsView(Interface):
    """
    Sitemap view interface
    """

    sitemaps = Attribute("Returns mapping of sitemap's type to list of "
                         "appropriate objects")
    hasContentSM = Attribute("Returns boolean about existance of content "
                             "sitemap")
    hasMobileSM = Attribute("Returns boolean about existance of mobile "
                            "sitemap")
    hasNewsSM = Attribute("Returns boolean about existance of news sitemap")
    sm_types = Attribute("List of sitemap types")

    def sitemapsDict():
        """ Return dictionary like object with data for table
        """
    def sitemapsURLByType():
        """ Return dictionary like object with sitemap_type as key
            and sitemap object(s) as value
        """
    def getVerificationFiles():
        """ Return list of existent verification files on site.
            Update googlesitemap_properties.verification_file
            property for only existent files
        """

    def uploadVerificationFile(vfile):
        """ Upload passed site verification file to the site.
            On success - update googlesitemaps verification files list.
            Return tuple where :
              1. boolean value - is verification file successfully created.
              2. string value:
                2.1. if successfull - id of created verification file
                2.2. if failure - error descirption
        """


class ConfigletSettingsView(BrowserView):
    """
    Configlet settings browser view
    """
    implements(IConfigletSettingsView)
    sitemaps = []

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.tools = queryMultiAdapter((self.context, self.request),
                                       name="plone_tools")
        self.pps = queryMultiAdapter((self.context, self.request),
                                     name="plone_portal_state")
        self.sitemaps = [i.getObject() for i in
                         self.tools.catalog()(portal_type='Sitemap')]

    @property
    def sm_types(self):
        return [i.getSitemapType() for i in self.sitemaps]

    @property
    def hasContentSM(self):
        return 'content' in self.sm_types

    @property
    def hasMobileSM(self):
        return 'mobile' in self.sm_types

    @property
    def hasNewsSM(self):
        return 'news' in self.sm_types

    def sitemapsURLByType(self):
        sitemaps = {}
        for sm in self.sitemaps:
            smlist = sitemaps.setdefault(sm.getSitemapType(), [])
            smlist.append({'url': sm.absolute_url(), 'id': sm.id})

        sitemaps['all'] = sitemaps.setdefault('content', []) + \
            sitemaps.setdefault('mobile', []) + sitemaps.setdefault('news', [])
        return sitemaps

    def sitemapsURLs(self):
        sitemaps = {}
        for sm in self.sitemaps:
            smlist = sitemaps.setdefault(sm.getSitemapType(), [])
            smlist.append(sm.absolute_url())
        return sitemaps

    def sitemapsDict(self):
        content, mobile, news = [], [], []
        for sm in self.sitemaps:
            data = self.getSMData(sm)
            if data['sm_type'] == 'Content':
                content.append(data)
            elif data['sm_type'] == 'Mobile':
                mobile.append(data)
            elif data['sm_type'] == 'News':
                news.append(data)
        return content + mobile + news

    def getSMData(self, ob):
        size, entries = self.getSitemapData(ob)
        return {'sm_type': ob.getSitemapType().capitalize(),
                'sm_id': ob.id,
                'sm_url': ob.absolute_url(),
                'sm_size': size and splitNum(size) or '',
                'sm_entries': entries and splitNum(entries) or '',
                }

    def getSitemapData(self, ob):
        size, entries = (0, 0)
        view = ob and ob.defaultView() or None
        if view:
            self.request.RESPONSE
            bview = queryMultiAdapter((ob, self.request), name=view)
            if bview:
                try:
                    size = len(bview())
                    entries = bview.numEntries
                    self.request.RESPONSE.setHeader('Content-Type',
                                                    'text/html')
                except:
                    pass
        return (size, entries)

    def deleteGSMVerificationFile(self):
        portal = self.pps.portal()
        portal.manage_delObjects([self.request.id, ])
        self.request.RESPONSE.redirect(
            urlparse.urljoin(self.context.absolute_url,
                             'prefs_gsm_verification'))

    def getVerificationFiles(self):
        vfs = []
        props = getattr(self.tools.properties(), 'googlesitemap_properties')
        portal = self.pps.portal()
        if props:
            portal_ids = portal.objectIds()
            props_vfs = list(props.getProperty('verification_filenames', []))

            vfs = [vf for vf in props_vfs if vf in portal_ids]
            if not props_vfs == vfs:
                props._updateProperty('verification_filenames', vfs)

        return [{'id': x, 'title': portal[x].title} for x in vfs]

    def uploadVerificationFile(self, request):
        vfilename = ""
        portal = self.pps.portal()
        try:
            comment = request.get("comment")
            vfile = request.get("verification_file")
            vfilename, vftitle = cookId("", "", vfile)
            portal.manage_addFile(id="", file=vfile, title=comment)
            portal[vfilename].manage_addProperty(
                'CreatedBy', 'quintagroupt.plonegooglesitemaps', 'string')
        except BadRequestException, e:
            return False, str(e)
        else:
            props = self.tools.properties().googlesitemap_properties
            vfilenames = list(props.getProperty('verification_filenames', []))
            vfilenames.append(vfilename)
            props.manage_changeProperties(verification_filenames=vfilenames)
        return True, vfilename
