import re
from DateTime import DateTime
from zope.component import getMultiAdapter
from plone.memoize.view import memoize
from quintagroup.plonegooglesitemaps.browser.commonview \
    import CommonSitemapView, implements, ISitemapView

reTrailingParenthtical = re.compile("\s*\(.*\)\s*", re.S)

formatDate = lambda d: DateTime(d).strftime("%Y-%m-%d")


class NewsSitemapView(CommonSitemapView):
    """
    News Sitemap browser view
    """
    implements(ISitemapView)

    @property
    def additional_maps(self):

        return (
            ('publication_date',
             lambda x: x.Date and formatDate(x.Date) or ""),
            ('keywords', lambda x: x.Subject and ', '.join(x.Subject) or ""),
            ('title', lambda x: x.Title or x.getId or x.id),
            ('name', lambda x: x.Title and
                reTrailingParenthtical.sub("", x.Title) or ""),
            ('language', lambda x: x.Language or self.default_language()),
            ('access', lambda x: x.gsm_access or ""),
            ('genres', lambda x: x.gsm_genres and
                ", ".join(x.gsm_genres) or ""),
            ('stock', lambda x: x.gsm_stock or ""),
        )

    @memoize
    def default_language(self):
        pps = getMultiAdapter((self.context, self.request),
                              name="plone_portal_state")
        return pps.default_language

    def getFilteredObjects(self):
        min_date = DateTime() - 3
        return self.portal_catalog(
            path=self.search_path,
            portal_type=self.context.getPortalTypes(),
            review_state=self.context.getStates(),
            effective={"query": min_date,
                       "range": "min"},
            is_default_page=False
        )
