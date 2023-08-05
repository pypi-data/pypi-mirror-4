# $Id$
"""
Testing... the test framework
"""

from Products.Collage.tests.base import CollageTestCase
from Products.Collage.tests import utils as ctc_utils

class UtilsTestCase(CollageTestCase):
    """We test utilities for testcases"""

    def testTestRequest(self):
        request = ctc_utils.TestRequest()
        request.set('dummy', 'stuff')
        self.failUnlessEqual(request.get('dummy'), 'stuff')
        return

    def testAddcollage(self):
        self.loginAsPortalOwner()
        foo_collage = ctc_utils.addCollage(self.portal, 'foo', 'Foo')
        self.failUnlessEqual(foo_collage.title_or_id(), 'Foo')
        return

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UtilsTestCase))
    return suite
