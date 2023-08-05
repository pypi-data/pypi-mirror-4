# $Id$

from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Archetypes import atapi
from Products.Archetypes.ReferenceEngine import Reference
try:
    from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
except ImportError:
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.ATContentTypes.content.base import ATCTContent

from Products.Collage.interfaces import ICollageAlias, IDynamicViewManager
from Products.Collage.content.common import LayoutContainer
from Products.Collage.utilities import CollageMessageFactory as _
from Products.Collage.utilities import isTranslatable

class CollageAliasReference(Reference):
    """We need our own reference class to have a custom target deletion hook
    that resets the alias layout.
    """
    def delHook(self, tool, sourceObject=None, targetObject=None):
        """Override standard delHook
        """
        manager = IDynamicViewManager(sourceObject)
        manager.setLayout(None)
        return


CollageAliasSchema = ATCTContent.schema.copy() + atapi.Schema((
    atapi.ReferenceField(
        name='target',
        mutator='set_target',
        accessor='get_target',
        referenceClass = CollageAliasReference,
        relationship='Collage_aliasedItem',
        multiValued = 0,
        allowed_types = (),
        widget=ReferenceBrowserWidget(
            label=_(u'label_alias_target', default="Selected target object"),
            startup_directory='/',
        ),
        keepReferencesOnCopy=True,
    ),
))

# we don't require any fields to be filled out
CollageAliasSchema['title'].required = False

# never show in navigation, also when its selected
CollageAliasSchema['excludeFromNav'].default = True

CollageAliasSchema['relatedItems'].widget.visible = {'edit':'invisible', 'view':'invisible'}

class CollageAlias(BrowserDefaultMixin, LayoutContainer, ATCTContent):
    __implements__ = (getattr(atapi.OrderedBaseFolder,'__implements__',()), \
                      getattr(BrowserDefaultMixin,'__implements__',()))

    implements(ICollageAlias)

    meta_type = 'CollageAlias'

    schema = CollageAliasSchema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    def indexObject(self):
        pass

    def reindexObject(self,idxs=[] ):
        pass

    def unindexObject(self):
        pass

    def get_target(self):
        res = self.getRefs(self.getField('target').relationship)
        if res:
            res = res[0]
        else:
            res = None
        if isTranslatable(res):
            lang = getToolByName(self, 'portal_languages').getPreferredLanguage()
            res = res.getTranslation(lang) or res
        return res

atapi.registerType(CollageAlias, 'Collage')
