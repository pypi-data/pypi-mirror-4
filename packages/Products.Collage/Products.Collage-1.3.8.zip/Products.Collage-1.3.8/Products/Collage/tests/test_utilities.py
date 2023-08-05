# $Id$
"""Testing Collage utilities"""

from Products.Collage.tests.base import CollageTestCase
from Products.Collage.tests import utils as ctc_utils
from Products.Collage import utilities as cu

class UtilitiesTestCase(CollageTestCase):
    def testGenerateNewId(self):
        self.loginAsPortalOwner()
        self.portal.REQUEST.environ['REQUEST_METHOD'] = 'POST'
        foo_collage = ctc_utils.addCollage(self.portal, 'foo', 'Foo')

        new_id = cu.generateNewId(foo_collage)
        self.failUnlessEqual(new_id, '1')

        foo_collage.restrictedTraverse('insert-row').insertRow()
        new_id = cu.generateNewId(foo_collage)
        self.failUnlessEqual(new_id, '2')

        foo_collage.restrictedTraverse('insert-row').insertRow()
        self.failUnlessEqual(foo_collage.objectIds()[-1], '2')

        foo_collage._delObject(foo_collage.objectIds()[0])
        new_id = cu.generateNewId(foo_collage)
        self.failUnlessEqual(new_id, '1')
        return

    def testIsTranslatable(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', 'doc', title="Doc")
        doc = getattr(self.portal, 'doc')
        if cu.HAS_LINGUAPLONE:
            self.failUnless(cu.isTranslatable(doc))
        else:
            self.failIf(cu.isTranslatable(doc))
        return

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UtilitiesTestCase))
    return suite
