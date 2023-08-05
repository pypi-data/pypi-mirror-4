# $Id$
"""
Testing... the test framework
"""
import time
from DateTime import DateTime

from Products.Collage.tests.base import CollageTestCase
from Products.Collage.tests import utils as ctc_utils

from Products.Collage.browser.renderer import SimpleContainerRenderer
from Products.Collage.browser.renderer import WithPublishDateRenderer

class SimpleContainerRendererTestCase(CollageTestCase):
    """We test utilities for testcases"""

    def afterSetUp(self):
        _ = self.folder.invokeFactory(id='collage', type_name='Collage')
        self.collage = self.folder[_]
        _ = self.collage.invokeFactory(id='row', type_name='CollageRow')
        self.row = self.collage[_]
        _ = self.row.invokeFactory(id='column', type_name='CollageColumn')
        self.column = self.row[_]
        _ = self.column.invokeFactory(id='alias', type_name='CollageAlias')
        self.alias = self.column[_]

        _ = self.folder.invokeFactory(id='doc', type_name='Document')
        self.doc = self.folder[_]
        self.alias.set_target(self.doc.UID())

    def _makeOne(self, context):
        request = self.app.REQUEST
        return SimpleContainerRenderer(context, request)

    def test_getItemsCollage(self):
        view = self._makeOne(self.collage)
        items = view.getItems()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].__name__, 'standard')

    def test_getItemsRow(self):
        view = self._makeOne(self.row)
        items = view.getItems()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].__name__, 'standard')

    def test_getItemsColumn(self):
        view = self._makeOne(self.column)
        items = view.getItems()
        self.assertEqual(items[0].__name__, 'standard')


class WithPublishDateRendererTestCase(SimpleContainerRendererTestCase):

    def _makeOne(self, context):
        request = self.app.REQUEST
        return WithPublishDateRenderer(context, request)

    def test_rowfilter(self):
        view = self._makeOne(self.collage)
        items = view.getItems()
        self.assertEqual(len(items), 1)

        tomorrow = DateTime() + 1

        self.row.setEffectiveDate(tomorrow)
        items = view.getItems()
        self.assertEqual(len(items), 0)

    def test_columnfilter(self):
        view = self._makeOne(self.row)
        items = view.getItems()
        self.assertEqual(len(items), 1)

        yesterday = DateTime() - 1

        self.column.setExpirationDate(yesterday)
        items = view.getItems()
        self.assertEqual(len(items), 0)


    def test_itemfilter(self):
        now = DateTime()
        nearfuture = now  + 1/86400.0 * 2    # 2 seconds ahead of now
        self.doc.setEffectiveDate(nearfuture)
        view = self._makeOne(self.column)
        items = view.getItems()
        self.assertEqual(len(items), 0)

        time.sleep(2)  # wait for the document to appear

        items = view.getItems()
        self.assertEqual(len(items), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(SimpleContainerRendererTestCase))
    suite.addTest(makeSuite(WithPublishDateRendererTestCase))
    return suite
