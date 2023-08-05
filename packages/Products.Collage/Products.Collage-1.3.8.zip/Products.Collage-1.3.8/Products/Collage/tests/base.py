"""
Common testing resources
"""
from Testing import ZopeTestCase

ZopeTestCase.installProduct('Collage')

from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite(products=('Collage',))


class CollageTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()

class CollageFunctionalTestCase(PloneTestCase.FunctionalTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.FunctionalTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
