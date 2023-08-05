from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig

class CollectiveGroupmail(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.groupmail
        xmlconfig.file('configure.zcml',
                       collective.groupmail,
                       context=configurationContext)


    def setUpPloneSite(self, portal):
        pass

COLLECTIVE_GROUPMAIL_FIXTURE = CollectiveGroupmail()
COLLECTIVE_GROUPMAIL_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(COLLECTIVE_GROUPMAIL_FIXTURE, ),
                       name="CollectiveGroupmail:Integration")