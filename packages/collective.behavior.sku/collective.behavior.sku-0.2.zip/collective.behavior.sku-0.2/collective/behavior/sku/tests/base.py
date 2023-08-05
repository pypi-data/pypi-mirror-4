"""Base module for unittesting"""
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer

import unittest


class BehaviorSKULayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import collective.behavior.sku
        self.loadZCML(package=collective.behavior.sku)
        import collective.behavior.sku.tests.dexterity
        self.loadZCML(package=collective.behavior.sku.tests.dexterity)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.behavior.sku:default')
        self.applyProfile(portal, 'collective.behavior.sku.tests.dexterity:default')

    def tearDownZope(self, app):
        """Tear down Zope."""


FIXTURE = BehaviorSKULayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="BehaviorSKULayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="BehaviorSKULayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
