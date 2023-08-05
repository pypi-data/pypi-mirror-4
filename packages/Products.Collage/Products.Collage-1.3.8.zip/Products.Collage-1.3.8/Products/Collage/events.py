# -*- coding: utf-8 -*-
# $Id$
"""Zope 3 style event handlers"""

from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from Products.CMFCore.interfaces import IContentish
from Products.Collage.interfaces import ICollageAlias

@adapter(ICollageAlias, IObjectModifiedEvent)
def updateCollageAliasLayout(context, event):
    """Updating alias layout on alias changed
    """
    target = context.get_target()
    if target:
        layout = target.getLayout()
        context.setLayout(layout)

@adapter(IContentish, IObjectModifiedEvent)
def reindexOnModify(content, event):
    """Collage subcontent change triggers Collage reindexing
    """
    try:
        helper = content.restrictedTraverse('@@collage_helper')
    except AttributeError:
        return # content likely doesn't have REQUEST
    collage = helper.getCollageObject()
    if collage:
        # Change done in a Collage subobject
        collage.reindexObject()
