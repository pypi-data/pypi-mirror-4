# -*- coding: utf-8 -*-
"""Tests for enable_member action."""

from DateTime import DateTime
from niteoweb.ipn.core.interfaces import IIPN
from niteoweb.ipn.core.interfaces import IMemberEnabledEvent
from niteoweb.ipn.core.testing import IntegrationTestCase
from plone import api
from zope.component import eventtesting
from zope.component import queryAdapter
from zope.testing.loggingsupport import InstalledHandler

import mock


class TestConstraints(IntegrationTestCase):
    """Test different constraints on enable_member() action."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.ipn = queryAdapter(self.portal, IIPN)

        # create a test product group and set it's validity
        api.group.create(groupname='ipn_1')
        group = api.group.get(groupname='ipn_1')
        group.setGroupProperties(mapping={'validity': 31})

    def test_required_parameters(self):
        """Test that parameters are required."""
        from niteoweb.ipn.core.interfaces import MissingParamError

        with self.assertRaises(MissingParamError) as cm:
            self.ipn.enable_member(
                email=None,
                product_id='1',
                trans_type='SALE',
            )
        self.assertEquals(
            cm.exception.message,
            "Parameter 'email' is missing.",
        )

        with self.assertRaises(MissingParamError) as cm:
            self.ipn.enable_member(
                email='new@test.com',
                product_id=None,
                trans_type='SALE',
            )
        self.assertEquals(
            cm.exception.message,
            "Parameter 'product_id' is missing.",
        )

        with self.assertRaises(MissingParamError) as cm:
            self.ipn.enable_member(
                email='new@test.com',
                product_id='1',
                trans_type=None,
            )
        self.assertEquals(
            cm.exception.message,
            "Parameter 'trans_type' is missing.",
        )

    def test_product_group_parameter(self):
        """Test that product_group parameter is checked for validity."""
        from niteoweb.ipn.core.interfaces import InvalidParamValueError

        with self.assertRaises(InvalidParamValueError) as cm:
            self.ipn.enable_member(
                email='new@test.com',
                product_id='0',
                trans_type='SALE',
            )
        self.assertEquals(
            cm.exception.message,
            "Could not find group with id '0'.",
        )

    def test_parameters_when_creating_a_new_member(self):
        """Test that 'affiliate' and 'fullname' parameters are required when
        member that is to be enabled does not exist yet."""
        from niteoweb.ipn.core.interfaces import MissingParamError

        with self.assertRaises(MissingParamError) as cm:
            self.ipn.enable_member(
                email='new@test.com',
                product_id='1',
                trans_type='SALE',
                fullname=None,
                affiliate='aff@test.com',
            )
        self.assertEquals(
            cm.exception.message,
            "Parameter 'fullname' is needed to create a new member.",
        )

        with self.assertRaises(MissingParamError) as cm:
            self.ipn.enable_member(
                email='new@test.com',
                product_id='1',
                trans_type='SALE',
                fullname='New Member',
                affiliate=None,
            )
        self.assertEquals(
            cm.exception.message,
            "Parameter 'affiliate' is needed to create a new member.",
        )

    def test_product_validity_parameter(self):
        """Product validity, which is read from the product group, must be a
        positive integer."""
        from niteoweb.ipn.core.interfaces import InvalidParamValueError

        group = api.group.get(groupname='ipn_1')
        group.setGroupProperties(mapping={'validity': 0})

        with self.assertRaises(InvalidParamValueError) as cm:
            self.ipn.enable_member(
                email='new@test.com',
                product_id='1',
                trans_type='SALE',
                fullname='New Member',
                affiliate='aff@test.com',
            )
        self.assertEquals(
            cm.exception.message,
            "Validity for group 'ipn_1' is not a positive integer: 0",
        )


class TestEnableMember(IntegrationTestCase):
    """Test runtime flow through the enable_member() action for most common
    use cases.
    """

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.ipn = queryAdapter(self.portal, IIPN)
        self.log = InstalledHandler('niteoweb.ipn.core')
        eventtesting.setUp()

        # create a test product group and set it's validity
        api.group.create(groupname='ipn_1')
        group = api.group.get(groupname='ipn_1')
        group.setGroupProperties(mapping={'validity': 31})

    def tearDown(self):
        """Clean up after yourself."""
        self.log.clear()
        eventtesting.clearEvents()

    @mock.patch('niteoweb.ipn.core.ipn.DateTime')
    def test_enable_new_member(self, DT):
        """Test creating a new member with enable_member() action."""
        DT.return_value = DateTime('2012/01/01')

        self.ipn.enable_member(
            email='new@test.com',
            product_id='1',
            trans_type='SALE',
            fullname='New Member',
            affiliate='aff@test.com',
        )

        # test member exists
        member = api.user.get(username='new@test.com')
        self.assertTrue(member)

        # test member properties set correctly
        self.assertEqual(member.getProperty('product_id'), '1')
        self.assertEqual(member.getProperty('fullname'), 'New Member')
        self.assertEqual(member.getProperty('affiliate'), 'aff@test.com')

        # test member is in product group
        self.assertIn(
            'new@test.com',
            [user.id for user in api.user.get_users(groupname='ipn_1')]
        )

        # test member valid_to
        self.assertEqual(
            api.user.get(username='new@test.com').getProperty('valid_to'),
            DateTime('2012/02/01')
        )

        # test event emitted
        events = list(set(eventtesting.getEvents(IMemberEnabledEvent)))
        self.assertEquals(len(events), 1)
        self.assertEquals(events[0].username, 'new@test.com')

        # test member history
        self.assert_member_history(
            username='new@test.com',
            history=['2012/01/01 00:00:00|enable_member|1|SALE|']
        )

        # test log output
        self.assertEqual(len(self.log.records), 5)
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "START enable_member:SALE for 'new@test.com'.",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "Creating a new member: new@test.com",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "Added member 'new@test.com' to product group 'ipn_1'.",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "Member's (new@test.com) valid_to date set to 2012/02/01.",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "END enable_member:SALE for 'new@test.com'.",
        )

    @mock.patch('niteoweb.ipn.core.ipn.DateTime')
    def test_enable_enabled_member(self, DT):
        """Test enabling an already enabled member, meaning extending its
        validity period."""
        DT.return_value = DateTime('2012/01/01')

        # first create a valid member
        self.test_enable_new_member()

        # now let's say a month goes by and the member pays the recurring fee
        DT.return_value = DateTime('2012/02/01')
        self.ipn.enable_member(
            email='new@test.com',
            product_id='1',
            trans_type='RECUR',
        )

        # test member valid_to
        self.assertEqual(
            api.user.get(username='new@test.com').getProperty('valid_to'),
            DateTime('2012/03/03')
        )

        # test event emitted
        events = list(set(eventtesting.getEvents(IMemberEnabledEvent)))
        self.assertEquals(len(events), 2)
        self.assertEquals(events[0].username, 'new@test.com')
        self.assertEquals(events[1].username, 'new@test.com')

        # test member history
        self.assert_member_history(
            username='new@test.com',
            history=[
                '2012/01/01 00:00:00|enable_member|1|SALE|',
                '2012/02/01 00:00:00|enable_member|1|RECUR|',
            ],
        )

        # test log output
        self.assertEqual(len(self.log.records), 3)
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "START enable_member:RECUR for 'new@test.com'.",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "Member's (new@test.com) valid_to date set to 2012/03/03.",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "END enable_member:RECUR for 'new@test.com'.",
        )

    @mock.patch('niteoweb.ipn.core.ipn.DateTime')
    def test_enable_disabled_member(self, DT):
        """Test enabling a previously disabled member."""
        DT.return_value = DateTime('2012/01/01')

        # first create a disabled member
        api.user.create(email='disabled@test.com')
        api.group.add_user(groupname='disabled', username='disabled@test.com')
        api.user.revoke_roles(
            username='disabled@test.com',
            roles=['Member', ]
        )

        self.ipn.enable_member(
            email='disabled@test.com',
            product_id='1',
            trans_type='UNCANCEL',
        )

        # test member is no longer in Disabled group
        self.assertNotIn(
            'disabled',
            [g.id for g in api.group.get_groups(username='disabled@test.com')]
        )

        # test member has Member role
        self.assertIn(
            'Member',
            api.user.get_roles(username='disabled@test.com'),
        )

        # test member valid_to
        self.assertEqual(
            api.user.get(username='disabled@test.com').getProperty('valid_to'),
            DateTime('2012/02/01')
        )

        # test event emitted
        events = list(set(eventtesting.getEvents(IMemberEnabledEvent)))
        self.assertEquals(len(events), 1)
        self.assertEquals(events[0].username, 'disabled@test.com')

        # test member history
        self.assert_member_history(
            username='disabled@test.com',
            history=['2012/01/01 00:00:00|enable_member|1|UNCANCEL|']
        )

        # test log output
        self.assertEqual(len(self.log.records), 6)
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "START enable_member:UNCANCEL for 'disabled@test.com'.",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "Removing member 'disabled@test.com' from Disabled group.",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "Granting member 'disabled@test.com' the Member role.",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "Added member 'disabled@test.com' to product group 'ipn_1'.",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "Member's (disabled@test.com) valid_to date set to 2012/02/01.",
        )
        self.assert_log_record(
            'INFO',
            'test_user_1_',
            "END enable_member:UNCANCEL for 'disabled@test.com'.",
        )
