# $Id$

from AccessControl import ClassSecurityInfo

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi

from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import ATCTMixin
from Products.Collage.content.common import LayoutContainer, CommonCollageSchema

from Products.CMFPlone.interfaces import INonStructuralFolder

from Products.Collage.interfaces import ICollage

from zope.interface import implements

from Products.Collage.utilities import CollageMessageFactory as _

CollageSchema = atapi.BaseContent.schema.copy() + atapi.Schema((
    atapi.StringField(
        name='title',
        searchable=True,
        widget=atapi.StringWidget(
            label='Title',
            label_msgid='label_title',
            i18n_domain='plone',
        )
    ),

    atapi.TextField(
        name='description',
        searchable=True,
        widget=atapi.TextAreaWidget(
            label='Description',
            label_msgid='label_description',
            i18n_domain='plone',
        )
    ),
    atapi.BooleanField('show_title',
        accessor='getShowTitle',
        widget=atapi.BooleanWidget(
            label=_(u'label_show_title', default=u"Show title"),
            description=_(u'help_show_title', default=u"Show title in page composition.")),
        default=1,
        languageIndependent=True,
        schemata="settings"),

    atapi.BooleanField('show_description',
        accessor='getShowDescription',
        widget=atapi.BooleanWidget(
            label=_(u'label_show_description', default='Show description'),
            description=_(u'help_show_description', default=u"Show description in page composition.")),
        default=1,
        languageIndependent=True,
        schemata="settings"),

    atapi.BooleanField('index_subobjects',
        accessor='mustIndexSubobjects',
        default=False,
        languageIndependent=True,
        schemata="settings",
        widget=atapi.BooleanWidget(
            label=_(u'label_index_subobjects', default=u"Add collage contents in searchable text?"),
            description=_(u'help_index_subobjects',
                 default=u"Show this collage in results when searching for terms "
                          u"appearing in a contained item. "
                          u"Note: Checking this option may slow down the system "
                          u"while editing the collage."))
            )


))

CollageSchema = CollageSchema + CommonCollageSchema.copy()

# move description to main edit page
CollageSchema['description'].schemata = 'default'

# support show in navigation feature and at marshalling
# speciel case set folderish to False since we want related items to be used
finalizeATCTSchema(CollageSchema, folderish=False, moveDiscussion=False)

class Collage(LayoutContainer, ATCTMixin, atapi.OrderedBaseFolder):

    # FIXME: Do we always need Zope 2 style interfaces ?
    __implements__ = (getattr(atapi.OrderedBaseFolder,'__implements__',()),
                      getattr(ATCTMixin, '__implements__',()))

    schema = CollageSchema

    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    implements(ICollage, INonStructuralFolder)

    def SearchableText(self):
        return self.aggregateSearchableText()

atapi.registerType(Collage, 'Collage')
