from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender

from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import DisplayList

from quintagroup.plonegooglesitemaps.interfaces import INewsSitemapProvider


class ExtendableStringField(ExtensionField, StringField):
    """An extendable string field."""


class ExtendableLinesField(ExtensionField, LinesField):
    """An extendable string field."""

access_lst = ["Subscription", "Registration"]
genres_lst = ["PressRelease", "Satire", "Blog", "OpEd", "Opinion",
              "UserGenerated"]


class NewsExtender(object):
    adapts(INewsSitemapProvider)
    implements(ISchemaExtender)

    fields = [
        ExtendableStringField(
            "gsm_access",
            accessor="gsm_access",
            vocabulary=DisplayList(zip(["", ] + access_lst,
                                   ["Open access", ] + access_lst)),
            default="",
            schemata="GoogleSitemap",
            widget=SelectionWidget(
                label="Access",
                description="Specifies whether an article is available to "
                    "all readers (in case of the emtpy field, or only to "
                    "those with a free or paid membership to your site.",
                format="radio"),
        ),
        ExtendableLinesField(
            "gsm_genres",
            accessor="gsm_genres",
            vocabulary=DisplayList(zip(genres_lst, genres_lst)),
            schemata="GoogleSitemap",
            default=(),
            widget=MultiSelectionWidget(
                label="Genres",
                description="Select one or more properties for an article, "
                            "namely, whether it is a press release, "
                            "a blog post, an opinion, an op-ed piece, "
                            "user-generated content, or satire.",
                format="checkbox"),
        ),
        ExtendableStringField(
            "gsm_stock",
            accessor="gsm_stock",
            default="",
            schemata="GoogleSitemap",
            widget=StringWidget(
                label="Stock Tickers",
                description="A comma-separated list of up to 5 stock tickers "
                    "of the companies, mutual funds, or other financial "
                    "entities that are the main subject of the article. "
                    "Relevant primarily for business articles. Each ticker "
                    "must be prefixed by the name of its stock exchange, "
                    "and must match its entry in Google Finance. "
                    "For example, \"NASDAQ:AMAT\" (but not \"NASD:AMAT\"), "
                    "or \"BOM:500325\" (but not \"BOM:RIL\").",
                size=70),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
