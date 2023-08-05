"""Base module for unittesting"""

import unittest2 as unittest

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2


class CartCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""

        # Required by Products.CMFPlone:plone-content to setup defaul plone site.
        z2.installProduct(app, 'Products.PythonScripts')

        # Load ZCML
        import collective.cart.core
        self.loadZCML(package=collective.cart.core)
        z2.installProduct(app, 'collective.cart.core')

    def setUpPloneSite(self, portal):
        """Set up Plone."""

        # Installs all the Plone stuff. Workflows etc. to setup defaul plone site.
        self.applyProfile(portal, 'Products.CMFPlone:plone')

        # Install portal content. Including the Members folder! to setup defaul plone site.
        self.applyProfile(portal, 'Products.CMFPlone:plone-content')

        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.cart.core:default')

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'collective.cart.core')
        z2.uninstallProduct(app, 'Products.PythonScripts')


FIXTURE = CartCoreLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="CartCoreLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="CartCoreLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
