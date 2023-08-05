# -*- coding: utf-8 -*-
# $Id$

from ZODB.POSException import ConflictError

from OFS.CopySupport import _cb_decode
from OFS import Moniker

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Collage.interfaces import IDynamicViewManager
from Products.Collage.utilities import getCollageSiteOptions
from Products.Collage.utilities import CollageMessageFactory as _

from zope.component import getMultiAdapter, queryUtility

from plone.i18n.normalizer.interfaces import IIDNormalizer

class SimpleContentMenuViewlet(object):
    def isAlias(self):
        return getattr(self.__parent__, '__alias__', None) is not None

    def portal_url(self):
        return getToolByName(self.context, 'portal_url')()

    def getImmediateObject(self):
        """Returns the immediate object added to the Collage
        instead of a possible alias target object."""
        alias = getattr(self.__parent__, '__alias__', None)
        if alias:
            return alias.aq_inner

        return self.context.aq_inner

class LayoutViewlet(SimpleContentMenuViewlet):
    def getLayouts(self):
        context = self.context

        # handle aliased objects
        alias = getattr(self.__parent__, '__alias__', None)
        if alias: context = alias

        manager = IDynamicViewManager(context)

        # lookup active layout
        active = manager.getLayout()

        if not active:
            active, title = manager.getDefaultLayout()

        # compile list of registered layouts
        layouts = manager.getLayouts()

        # filter out fallback view
        layouts = filter(lambda (name, title): name != u'fallback', layouts)

        # make sure the active layout (which may not be available) is
        # included
        if active not in [name for name, title in layouts]:
            layouts.append(
                (active, _(u"Missing: $name", mapping={'name': active})))

        return [{
            'id': name,
            'name': title,
            'active': name == active} for (name, title) in layouts]

class SkinViewlet(SimpleContentMenuViewlet):
    def getSkins(self):
        context = self.context

        # handle aliased objects
        alias = getattr(self.__parent__, '__alias__', None)
        if alias: context = alias

        manager = IDynamicViewManager(context)

        # lookup active skin
        active = manager.getSkin()

        if not active:
            active = 'default'

        # compile list of registered skins for the layout
        skins = manager.getSkins(self.request)

        return [{'id': name,
                 'name': title,
                 'active': name == active} for (name, title) in skins]


class InsertNewItemViewlet(object):
    def normalizeString(self):
        return getToolByName(self.context, 'plone_utils').normalizeString

    def getAddableTypes(self):
        collage_options = getCollageSiteOptions()
        plone_view = self.context.restrictedTraverse('@@plone')
        container = plone_view.getCurrentFolder()
        idnormalizer = queryUtility(IIDNormalizer)

        #BBB Plone 4
        try:
            factories_view = getMultiAdapter((self.context, self.request),
                                             name='folder_factories')
            allowed_types = [i for i in factories_view.addable_types() if
                             collage_options.enabledType(i['id'])]

            return allowed_types
        except:
            portal_url = getToolByName(self.context, 'portal_url')()
            results = []
            for t in container.getAllowedTypes():
                if collage_options.enabledType(t.getId()):
                    cssId = idnormalizer.normalize(t.getId())
                    cssClass = 'contenttype-%s' % cssId
                    results.append({'title': t.Title(),
                                    'description': t.Description(),
                                    'icon': '%s/%s' % (portal_url, t.getIcon()),
                                    'extra': {'id' : cssId, 'separator' : None,
                                              'class' : cssClass},
                                    'id': t.getId()})

class SplitColumnViewlet(object):
    pass

class IconViewlet(SimpleContentMenuViewlet):
    def getIcon(self):
        tt = getToolByName(self.context, 'portal_types')
        obj_typeinfo = tt.getTypeInfo(self.context.portal_type)

        return obj_typeinfo.getIcon()

class ActionsViewlet(SimpleContentMenuViewlet):

    def getViewActions(self):
        plone_view = getMultiAdapter((self.context,self.request), name="plone")
        try:
            prepareObjectTabs = plone_view.prepareObjectTabs
        except AttributeError:
            provider = getMultiAdapter(
                (self.context, self.request, plone_view),
                name="plone.contentviews")
            viewlet = provider.__getitem__("plone.contentviews")
            prepareObjectTabs = viewlet.prepareObjectTabs
        return prepareObjectTabs()

class CopyViewlet(SimpleContentMenuViewlet):
    pass

class PasteViewlet(SimpleContentMenuViewlet):
    @property
    def clipboard_data_valid(self):
        cb_dataValid = getattr(self.context, 'cb_dataValid', None)

        if callable(cb_dataValid):
            return cb_dataValid()

    def _get_clipboard_item(self):
        cp = self.request.get('__cp')
        op, mdatas = _cb_decode(cp) # see OFS/CopySupport.py

        # just get the first item on the clipboard
        mdata = mdatas[0]
        m = Moniker.loadMoniker(mdata)

        app = self.context.getPhysicalRoot()
        try:
            ob = m.bind(app)
        except (ConflictError, AttributeError, KeyError, TypeError):
            return None

        return ob

    def render(self):
        """Only render if the clipboard contains an object that can
        be added to this container."""

        if self.clipboard_data_valid:
            # verify that we are allowed to paste this item here
            item = self._get_clipboard_item()

            if item:
                portal_type = item.portal_type
                allowed_types = self.context.allowedContentTypes()
                if portal_type in (t.getId() for t in allowed_types):
                    return self.index()

        return u''

    def clipboard_item_title(self):
        title = self._get_clipboard_item().title_or_id()
        return u'Paste "%s"' % safe_unicode(title)
