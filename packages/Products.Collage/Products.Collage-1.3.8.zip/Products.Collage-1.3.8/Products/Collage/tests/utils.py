"""
Misc utilities for testing
"""
from zope.interface import implements

from zope.annotation import IAttributeAnnotatable
from zope.publisher.browser import TestRequest as ZopeTestRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.browser import IBrowserRequest

class TestRequest(ZopeTestRequest):
    implements(IHTTPRequest, IAttributeAnnotatable, IBrowserRequest)

    def set(self, attribute, value):
        self._environ[attribute] = value

def addCollage(container, oid, title):
    """Adding an empty Collage obj"""
    container.invokeFactory('Collage', oid, title=title)
    collage = getattr(container, oid)
    return collage
