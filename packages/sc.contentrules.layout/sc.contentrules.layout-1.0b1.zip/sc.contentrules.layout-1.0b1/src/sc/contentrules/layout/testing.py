# -*- coding: utf-8 -*-

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import sc.contentrules.layout
        self.loadZCML(package=sc.contentrules.layout)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        pass


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE, ),
    name='sc.contentrules.layout:Integration')

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, ),
    name='sc.contentrules.layout:Functional')
