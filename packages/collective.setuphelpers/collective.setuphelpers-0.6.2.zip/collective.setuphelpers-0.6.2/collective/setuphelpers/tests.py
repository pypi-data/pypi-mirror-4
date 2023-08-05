from plone.testing import z2
from zope.configuration import xmlconfig
import unittest2 as unittest
import doctest

#from zope.testing import doctestunit
#from zope.component import testing
from plone.testing import layered
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer, FunctionalTesting

TEST_STRUCTURE = [
    {
        'id':'testfolder',
        'title':'Test folder',
        'transition':'publish',
        'type':'Folder',
        'subfolder': [
         {
            'id':'item1',
            'title':'Item 1',
            'type':'Document',
            'field_text':'Text body',
         }]
    }
]

class Layer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
       # Load ZCML
        import collective.setuphelpers
        xmlconfig.file('configure.zcml', collective.setuphelpers, context=configurationContext)
        z2.installProduct(app, 'collective.setuphelpers')

        self['test_structure'] = TEST_STRUCTURE


DOCTEST_LAYER = Layer()

FUNCTIONAL_TESTING = FunctionalTesting(
                        bases=(DOCTEST_LAYER,),
                        name="SetupHelpers:Functional"
                                    )



def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
         layered(doctest.DocFileSuite("../../README.txt"), layer=FUNCTIONAL_TESTING),
    ])
    return suite
