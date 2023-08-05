from Testing import ZopeTestCase

# Make the boring stuff load quietly
ZopeTestCase.installProduct('collective.MockMailHost')

from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite(products=('collective.MockMailHost', ))


class FunctionalTestCase(PloneTestCase.FunctionalTestCase):
    
    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.FunctionalTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
        
