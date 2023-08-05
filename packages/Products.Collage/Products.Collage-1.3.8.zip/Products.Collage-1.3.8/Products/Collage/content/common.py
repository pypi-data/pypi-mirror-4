# $Id$

from Products.Archetypes import atapi
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Collage.interfaces import ICollageColumn

class LayoutContainer(object):
    """
    Container that provides aggregate search and display
    functionality.
    """

    def canSetDefaultPage(self):
        """Based on RichDocument/content/richdocument.py
        This method, from ISelectableBrowserDefault, is used to check whether
        the 'Choose content item to use as deafult view' option will be
        presented. This makes sense for folders, but not for RichDocument, so
        always disallow.
        """
        return False

    def aggregateSearchableText(self):
        """Append references' searchable fields."""

        data = super(LayoutContainer, self).SearchableText()

        # Must we add subcontents texts?
        if ICollageColumn.providedBy(self):
            helper = self.restrictedTraverse('@@collage_helper')
            collage = helper.getCollageObject()
            if not collage.mustIndexSubobjects():
                return data

        data = [data]
        for child in self.contentValues():
            data.append(child.SearchableText())

        data = ' '.join(data)
        return data

from Products.ATContentTypes.content.schemata import ATContentTypeSchema
CommonCollageSchema = atapi.Schema((
    ATContentTypeSchema['excludeFromNav'].copy(),
    ATContentTypeSchema['relatedItems'].copy(),
))
