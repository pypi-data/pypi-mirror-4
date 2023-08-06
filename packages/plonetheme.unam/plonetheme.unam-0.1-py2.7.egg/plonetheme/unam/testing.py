from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from zope.configuration import xmlconfig


class Theming(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        #load ZCML
        import plonetheme.unam
        xmlconfig.file(
            'configure.zcml', plonetheme.unam, context=configurationContext)

    def setUpPloneSite(self, portal):
        pass

THEMING_FIXTURE = Theming()
THEMING_INTEGRATION_TESTING = IntegrationTesting(
    bases=(THEMING_FIXTURE,), name="Theming:Integration")
THEMING_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(THEMING_FIXTURE,), name="Theming:Functional")
