from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2


class SlcLinkCollection(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import slc.linkcollection
        self.loadZCML('configure.zcml', package=slc.linkcollection)

        z2.installProduct(app, 'slc.linkcollection')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'slc.linkcollection:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'slc.linkcollection')


SLC_LINKCOLLECTION_FIXTURE = SlcLinkCollection()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(SLC_LINKCOLLECTION_FIXTURE,),
    name="SlcLinkCollection:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SLC_LINKCOLLECTION_FIXTURE,),
    name="SlcLinkCollection:Functional")
