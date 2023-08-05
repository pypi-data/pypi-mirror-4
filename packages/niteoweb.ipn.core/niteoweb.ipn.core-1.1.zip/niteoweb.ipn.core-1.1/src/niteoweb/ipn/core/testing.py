# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from plone import api
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


class NiteowebIpnCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import niteoweb.ipn.core
        self.loadZCML(package=niteoweb.ipn.core)
        z2.installProduct(app, 'niteoweb.ipn.core')

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'niteoweb.ipn.core:default')

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ['Member'])
        login(portal, TEST_USER_NAME)

        # Create Disabled group
        api.group.create(groupname='Disabled')

        # Commit so that the test browser sees these objects
        portal.portal_catalog.clearFindAndRebuild()
        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'niteoweb.ipn.core')


FIXTURE = NiteowebIpnCoreLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="NiteowebIpnCoreLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="NiteowebIpnCoreLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING

    def assert_log_record(self, level, msg, name='niteoweb.ipn.core'):
        """Utility method for testing log output."""
        self.assertEqual(self.log.records[0].name, name)
        self.assertEqual(self.log.records[0].levelname, level)
        self.assertEqual(self.log.records[0].getMessage(), msg)
        self.log.records.pop(0)

    def assert_member_history(self, username, history):
        """Utility method for testing member history."""
        member = api.user.get(username=username)
        self.assertEqual(
            list(member.getProperty('history')),
            history,
        )


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
