"""Definition of the Sitemap content type
"""

import string
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName

from quintagroup.plonegooglesitemaps \
    import qPloneGoogleSitemapsMessageFactory as _
from quintagroup.plonegooglesitemaps.interfaces import ISitemap
from quintagroup.plonegooglesitemaps.config import SITEMAPS_VIEW_MAP, \
    PROJECTNAME, AVAILABLE_WF_SCRIPTS

SitemapSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField(
        name='sitemapType',
        storage=atapi.AnnotationStorage(),
        required=True,
        default='content',
        vocabulary=SITEMAPS_VIEW_MAP.keys(),
        widget=atapi.SelectionWidget(
            label=_(u"Sitemap type"),
            visible={'edit': 'invisible', 'view': 'invisible'},
            description=_(u"Select Type of the sitemap."),
        ),
    ),
    atapi.LinesField(
        name='portalTypes',
        storage=atapi.AnnotationStorage(),
        required=True,
        default=['Document', ],
        vocabulary_factory="plone.app.vocabularies.ReallyUserFriendlyTypes",
        #schemata ='default',
        widget=atapi.MultiSelectionWidget(
            label=_(u"Define the types"),
            description=_(u"Define the types to be included in sitemap."),
        ),
    ),
    atapi.LinesField(
        name='states',
        storage=atapi.AnnotationStorage(),
        required=True,
        default=['published', ],
        vocabulary="getWorkflowStates",
        #schemata ='default',
        widget=atapi.MultiSelectionWidget(
            label=_(u"Review status"),
            description=_(u"You may include items in sitemap depend of "
                          u"their review state."),
        ),
    ),
    atapi.LinesField(
        name='blackout_list',
        storage=atapi.AnnotationStorage(),
        required=False,
        #default='',
        #schemata ='default',
        widget=atapi.LinesWidget(
            label=_(u"Blackout entries"),
            description=_(
                u"Objects which match filter condition will be excluded "
                u"from the sitemap.Every record should follow the spec: "
                u"[<filter name>:]<filter arguments>. By default there are "
                u"\"id\" and \"path\" filters (\"id\" used if filter name "
                u"not specified). There is possibility to add new filters. "
                u"Look into README.txt of the "
                u"quintagroup.plonegooglesitemaps package."),
        ),
    ),
    atapi.LinesField(
        name='reg_exp',
        storage=atapi.AnnotationStorage(),
        required=False,
        #default='',
        #schemata ='default',
        widget=atapi.LinesWidget(
            label=_(u"URL processing Regular Expressions"),
            description=_(u"Provide regular expressions (in Perl syntax), "
                          u"one per line to be applied to URLs before "
                          u"including them into Sitemap. Example 1: "
                          u"\"s/\/index_html//\" will remove /index_html "
                          u"from URLs representing default documents. "
                          u"Example 2: "
                          u"\"s/[you_site\/internal\/path]/[domain]/\" will "
                          u"fix URLs in the sitemap in case they are "
                          u"generated on the basis of your site internal"
                          u"path rather than your site domain URL. "),
        ),
    ),

    atapi.LinesField(
        name='urls',
        storage=atapi.AnnotationStorage(),
        required=False,
        #default='',
        #schemata ='default',
        widget=atapi.LinesWidget(
            label=_(u"Additional URLs"),
            description=_(u"Define additional URLs that are not objects and "
                          u"that should be included in sitemap."),
        ),
    ),
    atapi.LinesField(
        name='pingTransitions',
        storage=atapi.AnnotationStorage(),
        required=False,
        vocabulary='getWorkflowTransitions',
        #schemata="default",
        widget=atapi.MultiSelectionWidget(
            label=_(u"Pinging workflow transitions"),
            description=_(u"Select workflow transitions for pinging "
                          u"google on."),
        ),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

SitemapSchema['id'].widget.ignore_visible_ids = True
SitemapSchema['title'].storage = atapi.AnnotationStorage()
SitemapSchema['title'].required = False
SitemapSchema['title'].widget.visible = {'edit': 'invisible',
                                         'view': 'invisible'}
SitemapSchema['description'].storage = atapi.AnnotationStorage()
SitemapSchema['description'].widget.visible = {'edit': 'invisible',
                                               'view': 'invisible'}

schemata.finalizeATCTSchema(SitemapSchema, moveDiscussion=False)
SitemapSchema['relatedItems'].schemata = 'metadata'
SitemapSchema['relatedItems'].widget.visible = {'edit': 'invisible',
                                                'view': 'invisible'}


class Sitemap(base.ATCTContent):
    """Search engine Sitemap content type"""
    implements(ISitemap)

    portal_type = "Sitemap"
    schema = SitemapSchema

    #title = atapi.ATFieldProperty('title')
    #description = atapi.ATFieldProperty('description')

    def at_post_create_script(self):
        # Set default layout on creation
        default_layout = SITEMAPS_VIEW_MAP[self.getSitemapType()]
        self._setProperty('layout', default_layout)

    def getWorkflowStates(self):
        pw = getToolByName(self, 'portal_workflow')
        states = list(set([v for k, v in pw.listWFStatesByTitle()]))
        states.sort()
        return atapi.DisplayList(zip(states, states))

    def getWorkflowTransitions(self):
        wf_trans = []
        pw = getToolByName(self, 'portal_workflow')
        for wf_id in pw.getWorkflowIds():
            wf = pw.getWorkflowById(wf_id)
            if not wf:
                continue
            for wf_tr in wf.transitions.values():
                if wf_tr.after_script_name in AVAILABLE_WF_SCRIPTS:
                    wf_trans.append(
                        ("%s#%s" % (wf_id, wf_tr.id),
                         "%s : %s (%s)" % (wf_id, wf_tr.id,
                                           wf_tr.title_or_id())))
        return atapi.DisplayList(wf_trans)

    def setPingTransitions(self, value, **kw):
        """Add 'Ping sitemap' afterscript for selected workflow transitions.
        """
        self.getField('pingTransitions').set(self, value)

    def setBlackout_list(self, value, **kw):
        """Clean-up whitespaces and empty lines."""
        val = filter(None, map(string.strip, value))
        self.getField('blackout_list').set(self, val)


atapi.registerType(Sitemap, PROJECTNAME)
