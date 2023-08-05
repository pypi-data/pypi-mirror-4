# -*- coding: utf-8 -*-

from zope.configuration import xmlconfig

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

class OcchielloSandboxLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import ospfe.occhiello
        xmlconfig.file('configure.zcml',
                       ospfe.occhiello,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ospfe.occhiello:default')
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager'])


OCCHIELLO_FIXTURE = OcchielloSandboxLayer()
OCCHIELLO_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(OCCHIELLO_FIXTURE, ),
                       name="Occhiello:Integration")
OCCHIELLO_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(OCCHIELLO_FIXTURE, ),
                      name="Occhiello:Functional")

