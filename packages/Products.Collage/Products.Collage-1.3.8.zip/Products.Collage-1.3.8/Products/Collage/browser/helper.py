# -*- coding: utf-8 -*-
# $Id$

from zope.interface import Interface

from Acquisition import aq_inner, aq_parent

from Products.Collage.interfaces import ICollage

class ICollageHelper(Interface):
    def isCollageContent():
        """True if the content item is in a Collage"""

    def getCollageObject():
        """Search object tree for a Collage object or None."""

    def getCollageObjectURL():
        """Search object tree for a Collage-object and return URL."""


class CollageHelper(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def isCollageContent(self, parent=None):
        return self.getCollageObject() is not None

    def getCollageObject(self, parent=None):
        if parent is None:
            parent = self.context

        while parent is not None:
            parent = aq_parent(aq_inner(parent))

            if ICollage.providedBy(parent):
                return parent

    def getCollageObjectURL(self, parent=None):
        collage = self.getCollageObject(parent)
        if collage:
            return collage.absolute_url()
        raise ValueError("Collage object not found.")
