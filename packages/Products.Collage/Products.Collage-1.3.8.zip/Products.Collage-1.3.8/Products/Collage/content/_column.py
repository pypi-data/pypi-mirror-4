# $Id$

from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.Collage.content.common import LayoutContainer,CommonCollageSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.Collage.interfaces import ICollageColumn

from zope.interface import implements

# CMFDynamicViewFTI imports
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Collage.utilities import CollageMessageFactory as _

CollageColumnSchema = atapi.BaseContent.schema.copy() + atapi.Schema((
    atapi.StringField(
        name='title',
        accessor='Title',
        required=False,
        searchable=True,
        widget=atapi.StringWidget(
            label=_(u'label_optional_column_title', default=u"Title"),
            description=_(u'help_optional_column_title',
                          default=u"You may optionally supply a title for this column."),
        )
    ),
))

CollageColumnSchema = CollageColumnSchema + CommonCollageSchema.copy()

# move description to main edit page
CollageColumnSchema['description'].schemata = 'default'

# never show row in navigation, also when its selected
CollageColumnSchema['excludeFromNav'].default = True

# support show in navigation feature and at marshalling
finalizeATCTSchema(CollageColumnSchema, folderish=True, moveDiscussion=False)

class CollageColumn(BrowserDefaultMixin, LayoutContainer, atapi.OrderedBaseFolder):

    # FIXME: Do we have to honour Zope 2 style interface?
    __implements__ = (getattr(atapi.OrderedBaseFolder,'__implements__',()), \
                      getattr(BrowserDefaultMixin,'__implements__',()))

    schema = CollageColumnSchema

    _at_rename_after_creation = True

    implements(ICollageColumn)

    security = ClassSecurityInfo()

    def SearchableText(self):
        return self.aggregateSearchableText()

    def indexObject(self):
        pass

    def reindexObject(self,idxs=[] ):
        pass

    def unindexObject(self):
        pass

atapi.registerType(CollageColumn, 'Collage')
