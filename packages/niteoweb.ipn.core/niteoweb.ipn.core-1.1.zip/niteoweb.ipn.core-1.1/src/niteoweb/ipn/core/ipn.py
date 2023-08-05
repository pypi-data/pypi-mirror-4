# -*- coding: utf-8 -*-
"""Module providing IPN actions."""

from DateTime import DateTime
from five import grok
from niteoweb.ipn.core import DISABLED
from niteoweb.ipn.core import PGI
from niteoweb.ipn.core.interfaces import IIPN
from niteoweb.ipn.core.interfaces import MemberDisabledEvent
from niteoweb.ipn.core.interfaces import MemberEnabledEvent
from niteoweb.ipn.core.interfaces import MissingParamError
from niteoweb.ipn.core.interfaces import InvalidParamValueError
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from zope.event import notify

import logging

logger = logging.getLogger("niteoweb.ipn.core")


class IPN(grok.MultiAdapter):
    """IPN actions."""
    grok.adapts(ISiteRoot)
    grok.implements(IIPN)

    def __init__(self, context):
        """Initialize the IPN portal adapter.

        :param context: Portal object.
        """
        self.context = context

    def enable_member(
        self,
        email=None,
        product_id=None,
        trans_type=None,
        fullname=None,
        affiliate=None,
    ):
        """Enable an existing or create a new member.

        :param email: Email of the member, also used as username.
        :type email: string
        :param product_id: ID of product that Member has purchased.
        :type product_id: string
        :param trans_type: Type of transaction that occurred.
        :type trans_type: string
        :param fullname: Member's fullname, required only when creating a new
            member.
        :type fullname: string
        :param affiliate: Member's affiliate, needed only when creating a new
            member.
        :type affiliate: string

        :returns: None

        """
        logger.info("START enable_member:%s for '%s'." % (trans_type, email))
        note = ''

        if not email:
            raise MissingParamError("Parameter 'email' is missing.")

        if not product_id:
            raise MissingParamError("Parameter 'product_id' is missing.")

        if not trans_type:
            raise MissingParamError("Parameter 'trans_type' is missing.")

        # Product group must exist
        product_group = api.group.get(groupname=PGI % product_id)
        if not product_group:
            raise InvalidParamValueError(
                "Could not find group with id '%s'." % product_id)

        # Create a member object if this is a new member
        if not api.user.get(username=email):

            if not fullname:
                raise MissingParamError(
                    "Parameter 'fullname' is needed to create a new member.")

            if not affiliate:
                raise MissingParamError(
                    "Parameter 'affiliate' is needed to create a new member.")

            logger.info("Creating a new member: %s" % email)
            properties = dict(
                product_id=product_id,
                fullname=fullname,
                affiliate=affiliate,
            )
            api.user.create(
                email=email,
                properties=properties,
            )
        member = api.user.get(username=email)

        # If an existing member is in group Disabled, remove him from there
        if DISABLED in [g.id for g in api.group.get_groups(user=member)]:
            logger.info(
                "Removing member '%s' from Disabled group." % member.id)
            api.group.remove_user(groupname=DISABLED, user=member)

        # Grant Member role if member does not have it yet
        if not 'Member' in api.user.get_roles(user=member):
            logger.info("Granting member '%s' the Member role." % member.id)
            api.user.grant_roles(user=member, roles=['Member'])

        # Add member to product group
        if product_group not in api.group.get_groups(user=member):
            api.group.add_user(user=member, group=product_group)
            logger.info(
                "Added member '%s' to product group '%s'."
                % (member.id, product_group)
            )

        # Set member's validity based on his product group
        product_validity = int(product_group.getProperty('validity'))
        if product_validity < 1:
            raise InvalidParamValueError(
                "Validity for group '%s' is not a positive integer: %i"
                % (product_group.id, product_validity))

        valid_to = DateTime() + product_validity
        member.setMemberProperties(mapping={'valid_to': valid_to})
        logger.info(
            "Member's (%s) valid_to date set to %s."
            % (member.id, valid_to.strftime('%Y/%m/%d')))

        # Add entry to member history
        self._add_to_member_history(
            member,
            '{timestamp}|{action}|{product_id}|{ttype}|{note}'.format(
                timestamp=DateTime().strftime('%Y/%m/%d %H:%M:%S'),
                product_id=product_id,
                ttype=trans_type,
                action='enable_member',
                note=note,
            )
        )

        # Notify third-party code that a member was enabled
        notify(MemberEnabledEvent(member.id))

        # Done!
        logger.info("END enable_member:%s for '%s'." % (trans_type, email))

    def disable_member(
        self,
        email=None,
        product_id=None,
        trans_type=None,
        **kwargs
    ):
        """Disable an existing member.

        :param email: Email of the member, also used as username.
        :type email: string
        :param product_id: ID of product that Member has purchased.
        :type product_id: string
        :param trans_type: Type of transaction that occurred.
        :type trans_type: string

        :returns: None

        """
        logger.info("START disable_member:%s for '%s'." % (trans_type, email))
        note = ''

        if not email:
            raise MissingParamError("Parameter 'email' is missing.")

        if not product_id:
            raise MissingParamError("Parameter 'product_id' is missing.")

        if not trans_type:
            raise MissingParamError("Parameter 'trans_type' is missing.")

        member = api.user.get(username=email)
        if not member:
            raise InvalidParamValueError(
                "Cannot disable a nonexistent member: '%s'." % email)

        # Move to Disabled group if not already there
        if not member in api.user.get_users(groupname=DISABLED):
            logger.info("Adding member '%s' to Disabled group." % member.id)
            api.group.add_user(groupname=DISABLED, user=member)

        # Remove member from all groups and add a note to history which groups
        other_groups = [g for g in api.group.get_groups(user=member)
                        if g.id not in [DISABLED, 'AuthenticatedUsers']]
        if other_groups:
            note = 'removed from groups: '
            for group in other_groups:
                logger.info(
                    "Removing member '%s' from group '%s'."
                    % (member.id, group.id)
                )
                api.group.remove_user(group=group, user=member)
                note += '%s, ' % group.id

        # Revoke 'Member' role which "disables" the user
        if 'Member' in api.user.get_roles(user=member):
            logger.info("Revoking member '%s' the Member role." % member.id)
            api.user.revoke_roles(user=member, roles=['Member'])

        # Add entry to member history
        self._add_to_member_history(
            member,
            '{timestamp}|{action}|{product_id}|{ttype}|{note}'.format(
                timestamp=DateTime().strftime('%Y/%m/%d %H:%M:%S'),
                product_id=product_id,
                ttype=trans_type,
                action='disable_member',
                note=note,
            )
        )

        # Notify third-party code that a member was enabled
        notify(MemberDisabledEvent(member.id))

        # Done!
        logger.info("END disable_member:%s for '%s'." % (trans_type, email))

    def _add_to_member_history(self, member, msg):
        """Add a record to member's history.

        :param msg: Message to add to member's history
        :type msg: string

        :returns: None

        """
        history = list(member.getProperty('history'))
        history.append(msg)
        member.setMemberProperties(mapping={'history': history})
