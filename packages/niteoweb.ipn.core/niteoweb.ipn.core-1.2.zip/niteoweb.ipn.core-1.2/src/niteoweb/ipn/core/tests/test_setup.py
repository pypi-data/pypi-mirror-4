# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from niteoweb.ipn.core.testing import IntegrationTestCase
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import mock


class TestInstall(IntegrationTestCase):
    """Test installation of niteoweb.ipn.core into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

    def test_product_installed(self):
        """Test if niteoweb.ipn.core is installed in portal_quickinstaller."""
        installer = api.portal.get_tool('portal_quickinstaller')
        self.assertTrue(installer.isProductInstalled('niteoweb.ipn.core'))

    def test_uninstall(self):
        """Test if niteoweb.ipn.core is cleanly uninstalled."""
        installer = api.portal.get_tool('portal_quickinstaller')
        installer.uninstallProducts(['niteoweb.ipn.core'])
        self.assertFalse(installer.isProductInstalled('niteoweb.ipn.core'))

    # setuphandlers.py
    def test_validity_group_property_added(self):
        """Test that groups have a new 'validity' property."""
        groupdata = api.portal.get_tool('portal_groupdata')
        self.assertTrue(groupdata.hasProperty('validity'))

    # setuphandlers.py
    def test_disabled_group_created(self):
        """Test that Disabled group was created."""
        self.assertTrue(api.group.get(groupname='Disabled'))

    # registry.xml
    def test_record_validity_secret(self):
        """Test that the validity.secret record is in the registry."""
        registry = getUtility(IRegistry)
        record_secretkey = registry.records[
            'niteoweb.ipn.core.validity.secret']
        self.assertEquals(record_secretkey.value, 'secret')

    # propertiestool.xml
    def test_portal_tabs_auto_creation_disabled(self):
        """Test if portal tabs auto-creation is disabled."""
        self.assertTrue(
            self.portal.portal_properties.
            site_properties.use_email_as_login
        )

    # memberdata_properties.xml
    def test_fields_added_to_member(self):
        """Test that extra fields are added to member properties."""
        memberdata = self.portal.portal_memberdata

        self.assertTrue(hasattr(memberdata, 'product_id'))
        self.assertEquals(
            str(memberdata.getProperty('product_id').__class__),
            "<type 'str'>"
        )

        self.assertTrue(hasattr(memberdata, 'affiliate'))
        self.assertEquals(
            str(memberdata.getProperty('affiliate').__class__),
            "<type 'str'>"
        )

        self.assertTrue(hasattr(memberdata, 'valid_to'))
        self.assertEquals(
            str(memberdata.getProperty('valid_to').__class__),
            'DateTime.DateTime.DateTime'
        )

        self.assertTrue(hasattr(memberdata, 'history'))
        self.assertEquals(
            str(memberdata.getProperty('history').__class__),
            "<type 'tuple'>"
        )


class TestDoubleInstall(TestInstall):
    """Test that setuphandlers.py code is resilient against installing this
    package multiple times.
    """

    def test(self):
        """Custom shared utility setup for tests."""
        # product already installed, so let's just run setupVarious
        # to make sure it doesn't break
        from niteoweb.ipn.core.setuphandlers import setupVarious
        context = mock.MagicMock(name='readDataFile')
        setupVarious(context)

        self.test_disabled_group_created()
        self.test_validity_group_property_added
