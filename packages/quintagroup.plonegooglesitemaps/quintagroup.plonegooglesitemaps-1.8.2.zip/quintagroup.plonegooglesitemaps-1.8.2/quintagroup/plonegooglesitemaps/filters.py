from itertools import ifilter
from zope.interface import implements
from zope.component import queryMultiAdapter
from quintagroup.plonegooglesitemaps.interfaces import IBlackoutFilter


class IdBlackoutFilter(object):
    """Filter-out by ID."""

    implements(IBlackoutFilter)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def filterOut(self, fdata, fargs):
        """Filter-out fdata list by id in fargs."""
        return ifilter(lambda b, fa=fargs: (b.getId or b.id) != fargs,
                       fdata)


class PathBlackoutFilter(object):
    """Filter-out by PATH."""

    implements(IBlackoutFilter)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def filterOut(self, fdata, fargs):
        """Filter-out fdata list by path in fargs."""
        if fargs.startswith("/"):
            # absolute path filter
            portal_id = queryMultiAdapter((self.context, self.request),
                                          name=u"plone_portal_state"
                                          ).portal().getId()
            test_path = '/' + portal_id + fargs
        elif fargs.startswith("./"):
            # relative path filter
            container_path = '/'.join(self.context.getPhysicalPath()[:-1])
            test_path = container_path + fargs[1:]
        else:
            # unrecognized starting point
            return fdata

        return ifilter(lambda b, tp=test_path: b.getPath() != tp,
                       fdata)
