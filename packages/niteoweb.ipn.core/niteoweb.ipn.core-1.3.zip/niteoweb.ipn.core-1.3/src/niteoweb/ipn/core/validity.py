# -*- coding: utf-8 -*-
"""View for finding expired members and disabling them."""

from DateTime import DateTime
from five import grok
from niteoweb.ipn.core import DISABLED
from niteoweb.ipn.core.interfaces import IIPN
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getAdapter

import logging

logger = logging.getLogger("niteoweb.ipn.core")


class Validity(grok.View):
    """Find members with expired validity and disable them."""
    grok.context(ISiteRoot)
    grok.require('zope2.View')

    def render(self):
        """Check for expired members and disable them."""
        messages = ['START validity check.']

        secret = api.portal.get_registry_record(
            'niteoweb.ipn.core.validity.secret')
        if self.request.get('secret') != secret:
            return "Wrong secret. Please configure it in control panel."

        ipn = getAdapter(self.context, IIPN)
        now = DateTime()

        for member in api.user.get_users():

            if DISABLED in [g.id for g in api.group.get_groups(user=member)]:
                continue  # already disabled

            valid_to = member.getProperty('valid_to')
            if valid_to < now:
                messages.append(
                    "Disabling member '%s' (%s)."
                    % (member.id, valid_to.strftime('%Y/%m/%d'))
                )
                if not self.request.get('dry-run'):
                    ipn.disable_member(
                        email=member.id,
                        product_id=member.getProperty('product_id'),
                        trans_type='cronjob',
                    )
        return '\n'.join(messages)
