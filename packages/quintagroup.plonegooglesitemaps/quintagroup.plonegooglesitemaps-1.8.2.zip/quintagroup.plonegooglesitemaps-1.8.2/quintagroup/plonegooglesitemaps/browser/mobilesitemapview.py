from DateTime import DateTime
from quintagroup.plonegooglesitemaps.browser.commonview \
    import CommonSitemapView, implements, ISitemapView

MOBILE_INTERFACES = ['quintagroup.mobileextender.interfaces.IMobile', ]


class MobileSitemapView(CommonSitemapView):
    """
    Mobile Sitemap browser view
    """
    implements(ISitemapView)

    additional_maps = (
        ('modification_date',
         lambda x: x.sitemap_date or DateTime(x.ModificationDate).HTML4()),
    )

    def getFilteredObjects(self):
        return self.portal_catalog(
            path=self.search_path,
            portal_type=self.context.getPortalTypes(),
            review_state=self.context.getStates(),
            object_provides=MOBILE_INTERFACES,
            is_default_page=False,
        )
