# -*- coding: utf-8 -*-
"""Tests for @@validity view."""

from DateTime import DateTime
from niteoweb.ipn.core.interfaces import IIPN
from niteoweb.ipn.core.interfaces import IMemberDisabledEvent
from niteoweb.ipn.core.testing import IntegrationTestCase
from plone import api
from plone.app.testing import logout
from plone.app.testing import TEST_USER_ID
from zope.component import eventtesting
from zope.component import queryAdapter
from zope.testing.loggingsupport import InstalledHandler

import mock


class TestValidity(IntegrationTestCase):
    """Test @@validity view."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.ipn = queryAdapter(self.portal, IIPN)
        self.log = InstalledHandler('niteoweb.ipn.core')
        eventtesting.setUp()

        # set a very long valid_to date for the test_user
        # in order to skip this one in our tests below
        test_user = api.user.get(username=TEST_USER_ID)
        test_user.setMemberProperties(
            mapping={'valid_to': DateTime('2020/01/01')})

    def tearDown(self):
        """Clean up after yourself."""
        self.log.clear()
        eventtesting.clearEvents()

    def test_wrong_secret(self):
        """Test secret is required to access @@validity."""
        view = self.portal.restrictedTraverse('validity')
        err_msg = "Wrong secret. Please configure it in control panel."

        # empty secret
        self.assertEquals(view.render(), err_msg)

        # wrong secret
        self.request['secret'] = 'wrong secret'
        self.assertEquals(view.render(), err_msg)

    def test_dry_run(self):
        """Test that member is not disabled if dry-run is set to True."""

        # first, let's create a member and enable it
        api.group.create(groupname='ipn_1')
        group = api.group.get(groupname='ipn_1')
        group.setGroupProperties(mapping={'validity': 31})
        self.ipn.enable_member(
            email='new@test.com',
            product_id='1',
            trans_type='SALE',
            fullname='New Member',
            affiliate='aff@test.com',
        )

        # run @@validity
        self.request['secret'] = 'secret'
        self.request['dry-run'] = True
        view = self.portal.restrictedTraverse('validity')
        view.render()

        # test member still has the Member role
        self.assertIn('Member', api.user.get_roles(username='new@test.com'))

        # test member is not in Disabled group
        self.assertNotIn(
            'disabled',
            [g.id for g in api.group.get_groups(username='new@test.com')]
        )

    @mock.patch('niteoweb.ipn.core.ipn.DateTime')
    def test_validity(self, DT):
        """Integration test of @@validity view."""
        DT.return_value = DateTime('2012/01/01')

        # first, let's create a member and enable it
        api.group.create(groupname='ipn_1')
        group = api.group.get(groupname='ipn_1')
        group.setGroupProperties(mapping={'validity': 31})
        self.ipn.enable_member(
            email='new@test.com',
            product_id='1',
            trans_type='SALE',
            fullname='New Member',
            affiliate='aff@test.com',
        )

        # clear after yourself before you start testing
        self.log.clear()
        eventtesting.clearEvents()

        # all is prepared, let's run @@validity as anonymous user, a
        # month after the initial sale
        logout()
        DT.return_value = DateTime('2012/02/02')
        self.request['secret'] = 'secret'
        view = self.portal.restrictedTraverse('validity')
        html = view.render()

        # test member is in Disabled group
        self.assertIn(
            'disabled',
            [g.id for g in api.group.get_groups(username='new@test.com')]
        )

        # test member is in no other group
        # TODO: for some reason api.group.remove_user does not work here
        # if I pass in "user=member" --> it is not removed from group???
        self.assertItemsEqual(
            ['disabled', 'AuthenticatedUsers', ],
            [g.id for g in api.group.get_groups(username='new@test.com')]
        )

        # test member does not have the Member role
        self.assertNotIn('Member', api.user.get_roles(username='new@test.com'))

        # test event emitted
        events = list(set(eventtesting.getEvents(IMemberDisabledEvent)))
        self.assertEquals(len(events), 1)
        self.assertEquals(events[0].username, 'new@test.com')

        # test member history
        self.assert_member_history(
            username='new@test.com',
            history=['2012/01/01 00:00:00|enable_member|1|SALE|',
                     '2012/02/02 00:00:00|disable_member|1|cronjob|'
                     'removed from groups: ipn_1, ']
        )

        # test HTML output
        self.assertEquals(
            html.split('\n'),
            [
                "START validity check.",
                "Disabling member 'new@test.com' (2012/02/01).",
            ]
        )

        # test log output
        self.assertEqual(len(self.log.records), 5)
        self.assert_log_record(
            'INFO',
            "START disable_member:cronjob for 'new@test.com'.",
        )
        self.assert_log_record(
            'INFO',
            "Adding member 'new@test.com' to Disabled group.",
        )
        self.assert_log_record(
            'INFO',
            "Removing member 'new@test.com' from group 'ipn_1'.",
        )
        self.assert_log_record(
            'INFO',
            "Revoking member 'new@test.com' the Member role.",
        )
        self.assert_log_record(
            'INFO',
            "END disable_member:cronjob for 'new@test.com'.",
        )
