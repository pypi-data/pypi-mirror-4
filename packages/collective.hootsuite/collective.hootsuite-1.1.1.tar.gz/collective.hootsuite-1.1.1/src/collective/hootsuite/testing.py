from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig

class CollectiveHootsuite(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.hootsuite
        xmlconfig.file('configure.zcml',
                       collective.hootsuite,
                       context=configurationContext)


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.hootsuite:default')

COLLECTIVE_HOOTSUITE_FIXTURE = CollectiveHootsuite()
COLLECTIVE_HOOTSUITE_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(COLLECTIVE_HOOTSUITE_FIXTURE, ),
                       name="CollectiveHootsuite:Integration")