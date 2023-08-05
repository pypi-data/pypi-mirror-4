# $Id$

from AccessControl import getSecurityManager, Unauthorized
try:
    from App.special_dtml import DTMLFile
except ImportError:
    from Globals import DTMLFile
from DateTime import DateTime

from zope.interface import directlyProvides
from zope.component import queryMultiAdapter
from zope.component import getMultiAdapter
from zope.component import ComponentLookupError

from Products.Five.browser import BrowserView

from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.utils import _checkPermission

from Products.Collage.interfaces import IDynamicViewManager
from Products.Collage.interfaces import ICollageAlias
from Products.Collage.utilities import isTranslatable
from Products.Collage.viewmanager import mark_request

class SimpleContainerRenderer(BrowserView):

    def getContents(self):
        return self.context.folderlistingFolderContents()

    def getItems(self, contents=None):
        """Items are a views to render.

        @param contents: If given fetch the folderListingFolderContents of
                         context.
        @return: a list of views ready to render.
        """
        # needed to circumvent bug :-(
        self.request.debug = False

        # transmute request interfaces
        ifaces = mark_request(self.context, self.request)

        views = []
        if contents is None:
            contents = self.getContents()
        for context in contents:
            if context is None:
                continue
            target = context
            manager = IDynamicViewManager(context)
            layout = manager.getLayout()

            if not layout:
                layout, title = manager.getDefaultLayout()

            if ICollageAlias.providedBy(context):
                target = context.get_target()

                # if not set, revert to context
                if target is None:
                    target = context

                # verify that target is accessible
                try:
                    getSecurityManager().validate(self, self, target.getId(), target)
                except Unauthorized:
                    continue

            # Filter out translation duplicates:
            # If a non-alias object is translatable, check if its language
            # is set to the currently selected language or to neutral,
            # or if it is the canonical version
            elif isTranslatable(target):
                language = self.request.get('LANGUAGE','')
                if target.Language() not in (language, ''):
                    # Discard the object, if it is not the canonical version
                    # or a translation is available in the requested language.
                    if not target.isCanonical() or target.getTranslation(language) in contents:
                        continue
                # If the target is a translation, get the layout defined on the canonical
                # object, unless a layout has already been defined on the translation.
                # Fallback to default layout.
                if not target.isCanonical():
                    canmanager = IDynamicViewManager(target.getCanonical())
                    layout = manager.getLayout() or canmanager.getLayout() or layout

            # don't assume that a layout is always available; note
            # that we can't use ``queryMultiAdapter`` because even
            # this lookup might fail hard
            try:
                view = getMultiAdapter((target, self.request), name=layout)
            except ComponentLookupError:
                view = getMultiAdapter(
                    (target, self.request), name='error_collage-view-not-found')
                view.notfoundlayoutname = layout

            # store reference to alias if applicable
            if ICollageAlias.providedBy(context):
                view.__alias__ = context

            views.append(view)

        # restore interfaces
        directlyProvides(self.request, ifaces)
        return views


class WithPublishDateRenderer(SimpleContainerRenderer):

    def getContents(self):
        show_inactive = _checkPermission(AccessInactivePortalContent, self)
        result = self.context.folderlistingFolderContents()
        if not show_inactive:
            def getItem(item):
                """ Return referenced object in case of an alias and the item itself otherwise
                """
                if ICollageAlias.providedBy(item):
                    return item.get_target()
                else:
                    return item

            now = DateTime()
            result = [item for item in result if getItem(item).effective() < now < getItem(item).expires()]
        return result


class CollageStylesheet(BrowserView):
    """Renders the collage standard stylesheet
    """
    template = DTMLFile('templates/collage.css', globals())

    def __call__(self, *args, **kwargs):
        """Renders the standard collage stylesheet.
        Note that we do not change HTTP headers since we are supposed to be
        published through the CSS registry
        """
        template = self.template.__of__(self.context)
        return template(context=self.context, request=self.request)
