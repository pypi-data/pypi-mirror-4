# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2

import unittest2 as unittest


class OshaQuizzesLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import osha.quizzes
        self.loadZCML(package=osha.quizzes)
        z2.installProduct(app, 'osha.quizzes')
        z2.installProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'osha.quizzes:default')

        # Login and create some test
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'folder')

        # Commit so that the test browser sees these objects
        portal.portal_catalog.clearFindAndRebuild()
        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'osha.quizzes')


FIXTURE = OshaQuizzesLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="OshaQuizzesLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="OshaQuizzesLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
