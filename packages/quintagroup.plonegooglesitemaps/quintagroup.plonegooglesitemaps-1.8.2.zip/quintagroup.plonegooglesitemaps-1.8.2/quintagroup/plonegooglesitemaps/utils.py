from urllib import quote as urlquote
from DateTime import DateTime
import logging
import urllib2
import socket

from Globals import DevelopmentMode
#from OFS.ObjectManager import BadRequestException
from Products.CMFCore.utils import getToolByName

from quintagroup.plonegooglesitemaps import config


logger = logging.getLogger(__name__)


# BBB: 'timeout' was added to urlopen in python2.6.
# Method dedicated to compatibility with python2.4 and python2.5
def urlopen(request, timeout=5.0, data=None, marker=[]):
    global_timeout = marker
    try:
        try:
            urllib2.urlopen(request, data, timeout=timeout)
        except TypeError, e:
            logger.info('TypeError: %s. You use python < 2.6. '
                        'Ugly socket.setdefaulttimeout hack applied '
                        'to avoid it upgrade your Plone.' % e)
            # socket.getdefaulttimeout() -> None.
            # It indicates that new socket objects have no timeout.
            global_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            urllib2.urlopen(request)
    finally:
        if global_timeout is not marker:
            socket.setdefaulttimeout(global_timeout)


def ping_google(plone_home, sitemap_relative_path):
    """Ping sitemap to Google"""
    resurl = plone_home + '/' + sitemap_relative_path

    if DevelopmentMode or config.testing:
        #prevent pinging in debug or testing mode
        print "Pinged %s sitemap to Google" % resurl
        return 0

    request = 'http://www.google.com/webmasters/tools/ping?sitemap=' +\
              urlquote(resurl)
    try:
        # BBB: Change urlopen -> socket.urlopen when
        # compatibility with python2.4 is not important
        g = urlopen(request)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            logger.error('We failed to reach a server. '
                         'Request: %s. '
                         'Reason: %s' % (request, e.reason))
        elif hasattr(e, 'code'):
            logger.error('The server couldn\'t fulfill the request. '
                         'Request: %s '
                         'Error code: %s. ' % (request, e.code))
    else:
        # Reading single byte should be enough for server pinged
        # to get our request, process it and send some response.
        g.read(1)
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
