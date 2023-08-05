# -*- coding: utf-8 -*-
# $Id$

from zope.component import getMultiAdapter
from zope.component import getUtility, queryUtility

try:
    from zope.schema.interfaces import IVocabularyFactory
except ImportError:
    from zope.app.schema.vocabulary import IVocabularyFactory

from plone.memoize.view import memoize_contextless
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.i18n.normalizer.interfaces import IIDNormalizer

from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone import PloneMessageFactory as p_
from Products.CMFPlone import utils
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

try:
    from Products.CMFPlone import Batch
except ImportError:
    from Products.CMFPlone.PloneBatch import Batch

from Products.Collage.browser.utils import escape_to_entities
from Products.Collage.utilities import getCollageSiteOptions
from Products.ZCTextIndex.ParseTree import ParseError

try:
    from plone.app.layout.navigation.interfaces import INavigationRoot
except ImportError:
    from Products.CMFPlone.interfaces import IPloneSiteRoot as INavigationRoot


from urllib import unquote


class ExistingItemsView(BrowserView):
    limit = 10

    def __call__(self):
        data = self._data()
        content = self.index(**data)

        # IE6 encoding bug workaround (IE6 sucks but...)
        if self.request.get('USER_AGENT', '').find('MSIE 6.0') > 0:
            # response must be latin-1
            self.request.RESPONSE.setHeader("Content-Type", "text/html; charset=ISO-8859-1")
            encoding = getSiteEncoding(self.context.context)
            if not isinstance(content, unicode):
                content = content.decode(encoding)

            # convert special characters to HTML entities since we're
            # recoding to latin-1
            content = escape_to_entities(content).encode('latin-1')

        return content

    @property
    def catalog(self):
        return getMultiAdapter((self.context, self.request),
                               name=u'plone_tools').catalog()

    @property
    def navigation_root(self):
        context = self.context.aq_inner
        while context is not None:
            if INavigationRoot.providedBy(context):
                break

            context = context.aq_parent

        return context

    def portal_url(self):
        return getMultiAdapter((self.context, self.request),
                               name=u'plone_portal_state').portal_url()

    @property
    def typefilter(self):
        options = getCollageSiteOptions()
        if not options.ref_browser_types:
            return list()
        ret = [{'title': '', 'value': '', 'selected': False}]
        factory = getUtility(IVocabularyFactory,
                         name=u'collage.vocabularies.CollageUserFriendlyTypes')
        for term in factory(self.context):
            if options.use_whitelist:
                if not term.value in options.alias_whitelist:
                    continue
            selected = self.request.form.get('portal_type') == term.value \
                and True or False
            ret.append({
                'title': term.title,
                'value': term.value,
                'selected': selected,
            })
        return ret

    def breadcrumbs(self):
        path = self.request.get('path')
        portal = self.navigation_root
        if path is None:
            context = portal
        else:
            context = portal.restrictedTraverse(unquote(path))
        crumbs = []
        context = aq_inner(context)
        while context is not None:
            if not IHideFromBreadcrumbs.providedBy(context):
                crumbs.append({
                    'path': "/".join(context.getPhysicalPath()),
                    'url': context.absolute_url(),
                    'title': context.title_or_id()
                    })
            if INavigationRoot.providedBy(context):
                break
            context = utils.parent(context)
        crumbs.reverse()
        return crumbs

    @memoize_contextless
    def listEnabledTypes(self):
        """Enabled types in a Collage as list of dicts.
        """
        actual_portal_type = self.request.get('portal_type', None)
        collage_options = getCollageSiteOptions()
        ttool = getToolByName(self.context, 'portal_types', None)
        if ttool is None:
            return None
        return [{'id': pt.getId(),
                 'title': p_(pt.Title()),
                 'selected': pt.getId() == actual_portal_type and 'selected' or None}
                for pt in ttool.listTypeInfo()
                if collage_options.enabledAlias(pt.getId())]

    @property
    def readitems(self):
        options = getCollageSiteOptions()
        if options.ref_browser_empty \
          and self.request.form.get('portal_type', '') == '' \
          and self.request.form.get('path', '') == '' \
          and self.request.form.get('b_start', None) is None:
            return False
        return True

    def _data(self):
        portal_types = self.request.get('portal_type', None)
        if not portal_types:
            portal_types = [pt['id'] for pt in self.listEnabledTypes()]
        query_path = self.request.get('path') or \
                     "/".join(self.navigation_root.getPhysicalPath())
        query_path = unquote(query_path)
        b_start = self.request.get('b_start', 0)
        query_text = unquote(self.request.get('SearchableText', ''))
        if query_text:
            depth = 10
        else:
            depth = 1
        if not self.readitems:
            results = []
        else:
            try:
                query = {'Language': 'all',
                         'portal_type': portal_types,
                         'path': {"query": query_path, 'depth': depth},
                         'sort_on': 'sortable_title',
                         'sort_order': 'ascending'}
                if query_text.strip():
                    query['SearchableText'] = query_text
                results = self.catalog(**query)
                # alternative: sort_order='reverse', sort_on='modified'
            except ParseError:
                results = []

        # setup description cropping
        cropText = getMultiAdapter(
            (self.context, self.request), name=u'plone').cropText
        props = getMultiAdapter((self.context, self.request),
                                name=u'plone_tools').properties()
        site_properties = props.site_properties
        desc_length = getattr(site_properties, 'search_results_description_length', 25)
        desc_ellipsis = getattr(site_properties, 'ellipsis', '...')

        items = []
        batch = Batch(results, self.limit, int(b_start), orphan=1)
        idnormalizer = queryUtility(IIDNormalizer)
        for result in batch:
            cssType = idnormalizer.normalize(result.portal_type)
            items.append({
                'UID': result.UID,
                'icon' : result.getIcon,
                'title': result.Title or result.getId,
                'description': cropText(result.Description, desc_length, desc_ellipsis),
                'type': result.Type,
                'folderish': result.is_folderish,
                'target_url': result.getURL(),
                'path': result.getPath(),
                'link_css_class': 'state-%s' % result.review_state,
                'cssType': 'contenttype-%s' % cssType,
                })

        return {
            'items': items,
            'batch': batch,
            'query': bool(query_text),
            'query_text': query_text,
            'path': query_path,
            }
