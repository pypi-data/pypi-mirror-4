from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.testing import z2

from zope.configuration import xmlconfig

class CollectiveGroupmail(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import z3c.jbot
        xmlconfig.file('configure.zcml', z3c.jbot, 
                        context=configurationContext)
        import collective.groupmail
        xmlconfig.file('configure.zcml',
                       collective.groupmail,
                       context=configurationContext)
        import collective.MockMailHost
        xmlconfig.file('configure.zcml',
                       collective.MockMailHost,
                       context=configurationContext)
        z2.installProduct(app, 'Products.PythonScripts')
        z2.installProduct(app, 'collective.MockMailHost')

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'Products.CMFPlone:plone')
        self.applyProfile(portal, 'Products.CMFPlone:plone-content')
        self.applyProfile(portal, 'collective.MockMailHost:default')

COLLECTIVE_GROUPMAIL_FIXTURE = CollectiveGroupmail()
COLLECTIVE_GROUPMAIL_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(COLLECTIVE_GROUPMAIL_FIXTURE, ),
                       name="CollectiveGroupmail:Integration")

COLLECTIVE_GROUPMAIL_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(COLLECTIVE_GROUPMAIL_FIXTURE, ),
                       name="CollectiveGroupmail:Functional")
