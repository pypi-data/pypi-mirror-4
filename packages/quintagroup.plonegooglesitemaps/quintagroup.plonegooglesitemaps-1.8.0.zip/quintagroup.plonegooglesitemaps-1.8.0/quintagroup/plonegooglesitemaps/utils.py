from urllib2 import urlopen
from urllib import quote as urlquote
from DateTime import DateTime

from Globals import DevelopmentMode
#from OFS.ObjectManager import BadRequestException
from Products.CMFCore.utils import getToolByName

from quintagroup.plonegooglesitemaps import config


def ping_google(url, sitemap_id):
    """Ping sitemap to Google"""

    resurl = url + "/" + sitemap_id

    if DevelopmentMode or config.testing:
        #prevent pinging in debug or testing mode
        print "Pinged %s sitemap to Google" % resurl
        return 0

    sitemap_url = urlquote(resurl)

    g = urlopen('http://www.google.com/webmasters/tools/ping?sitemap=' +
                sitemap_url)
    g.read()
    g.close()

    return 0


def getDefaultPage(obj):
    """ Method gets default page for object (folderish) """
    plone_tool = getToolByName(obj, 'plone_utils')
    return plone_tool.getDefaultPage(obj)


def isDefaultPage(obj):
    """ If object is default page then return True"""
    plone_tool = getToolByName(obj, 'plone_utils')
    return plone_tool.isDefaultPage(obj)


def dateTime(obj):
    """ Method gets modification date """
    return DateTime(obj.ModificationDate())
