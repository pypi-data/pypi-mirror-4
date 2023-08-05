# -*- coding: utf-8 -*-
# $Id$

from zope import event
from zope.lifecycleevent import ObjectModifiedEvent

from Products.Five.browser import BrowserView
from Products.CMFPlone import utils as cmfutils
from Products.Collage.utilities import CollageMessageFactory as _
from Products.Collage.utilities import generateNewId, findFirstAvailableInteger
from Products.Collage.interfaces import IDynamicViewManager

from plone.protect.postonly import check

def protect(func):
    def wrapper(self):
        check(self.request)
        return func(self)
    wrapper.__name__ = func.__name__
    return wrapper

class ActionsView(BrowserView):
    @protect
    def setDynamicView(self):
        layout = self.request['layout']

        manager = IDynamicViewManager(self.context)
        manager.setLayout(layout)

        self.context.plone_utils.addPortalMessage(_(u'View changed.'))
        self.request.response.redirect(self.context.REQUEST['HTTP_REFERER'])

    @protect
    def setDynamicSkin(self):
        skin = self.request['skin']

        manager = IDynamicViewManager(self.context)
        manager.setSkin(skin)

        self.context.plone_utils.addPortalMessage(_(u'Skin changed.'))
        self.request.response.redirect(self.context.REQUEST['HTTP_REFERER'])

    @protect
    def reorderObjects(self):
        object_id = self.request['id']
        position = self.request['position']

        if position.lower()=='up':
            self.context.moveObjectsUp(object_id)

        if position.lower()=='down':
            self.context.moveObjectsDown(object_id)

        if position.lower()=='top':
            self.context.moveObjectsToTop(object_id)

        if position.lower()=='bottom':
            self.context.moveObjectsToBottom(object_id)

        # order folder by field
        # id in this case is the field
        if position.lower()=='ordered':
            self.context.orderObjects(object_id)

        cmfutils.getToolByName(self.context, 'plone_utils').reindexOnReorder(self.context)
        return 1

    @protect
    def insertRow(self):
        # create row
        desired_id = generateNewId(self.context)
        row_id = self.context.invokeFactory(id=desired_id, type_name='CollageRow')
        row = getattr(self.context, row_id, None)
        row.setTitle('')

        # create column
        desired_id = generateNewId(row)
        col_id = row.invokeFactory(id=desired_id, type_name='CollageColumn')
        col = getattr(row, col_id, None)
        col.setTitle('')

        self.context.plone_utils.addPortalMessage(_(u'msg_row_added', default=u"Row was added."))
        self.request.response.redirect(self.context.REQUEST['HTTP_REFERER'])

    @protect
    def insertColumn(self):
        container = self.context
        desired_id = generateNewId(container)

        container.invokeFactory(id=desired_id, type_name='CollageColumn')

        self.context.plone_utils.addPortalMessage(_(u'msg_column_inserted', default="Column inserted."))
        self.request.response.redirect(self.context.REQUEST['HTTP_REFERER'])

    @protect
    def insertAlias(self):
        uid_catalog = cmfutils.getToolByName(self.context,
                                             'uid_catalog')

        uid = self.request.get('uid')
        container = self.context

        # check that target object exists
        brains = uid_catalog(UID=uid)
        if brains:
            # find first available id for the alias object
            ids = [i[6:] for i in container.objectIds() if i.startswith('alias-')]
            alias_id = 'alias-%s' % findFirstAvailableInteger(ids)

            # create new alias
            container.invokeFactory('CollageAlias', id=alias_id)
            alias = container[alias_id]

            # set target
            alias.set_target(uid)
            event.notify(ObjectModifiedEvent(alias))
            msg = _(u'msg_alias_inserted', default=u"Alias inserted.")
        else:
            msg = _(u'msg_target_object_not_found', default=u"Target object not found.")

        referer = self.request.get('HTTP_REFERER', self.context.absolute_url())
        self.context.plone_utils.addPortalMessage(msg)
        return self.request.RESPONSE.redirect(referer)

    @protect
    def deleteObject(self):
        parent = self.context.aq_inner.aq_parent
        parent.manage_delObjects(self.context.getId())
        fti = self.context.portal_types[self.context.portal_type]
        title = self.context.translate(fti.title, domain='plone')
        message = _(u'${title} deleted.', mapping={u'title' : title})
        self.context.plone_utils.addPortalMessage(message)
        self.request.response.redirect(self.context.REQUEST['HTTP_REFERER'])
