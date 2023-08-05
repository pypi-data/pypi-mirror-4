from zope.interface import Interface

from quintagroup.plonegooglesitemaps.utils import dateTime, getDefaultPage

#BBB: for compatibility with older plone versions
# (Plone 3.0, Plone 3.1, Plone3.2)
try:
    import plone.indexer
    indexer = plone.indexer.indexer
    IS_NEW = True
except ImportError:
    IS_NEW = False

    class IDummyInterface:
        pass

    class indexer:

        def __init__(self, *interfaces):
            self.interfaces = IDummyInterface,

        def __call__(self, callable):
            callable.__component_adapts__ = self.interfaces
            callable.__implemented__ = Interface
            return callable


@indexer(Interface)
def sitemap_date(obj, **kwargs):
    """ Method gets date for sitemap """

    def lastModificationDate(folderish_date, default_page):
        """  Method compares date (folderish object)
            with another date (default_page) and returns the last
        """

        # get modification date
        child_mdate = dateTime(default_page)

        if folderish_date > child_mdate:
            last_date = folderish_date
        else:
            last_date = child_mdate

        child = getDefaultPage(default_page)
        if not child:
            return last_date

        return lastModificationDate(last_date,
                                    default_page[child])

    default_page = getDefaultPage(obj)
    # get modification date
    date = dateTime(obj)
    if default_page:
        date = lastModificationDate(date, getattr(obj, default_page))

    return date.HTML4()

#BBB: for compatibility with older plone versions
# (Plone 3.0, Plone 3.1, Plone3.2)
if not IS_NEW:
    from Products.CMFPlone.CatalogTool import registerIndexableAttribute
    registerIndexableAttribute('sitemap_date', sitemap_date)
