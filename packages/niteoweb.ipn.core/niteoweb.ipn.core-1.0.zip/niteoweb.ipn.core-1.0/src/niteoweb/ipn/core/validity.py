# -*- coding: utf-8 -*-
"""View for finding expired members and disabling them."""

from DateTime import DateTime
from five import grok
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

        secret = api.portal.get_registry_record(
            'niteoweb.ipn.core.validity.secret')
        if self.request.get('secret') != secret:
            return "Wrong secret. Please configure it in control panel."

        ipn = getAdapter(self.context, IIPN)
        now = DateTime()
        for member in api.user.get_users():
            if member.getProperty('valid_to') < now:
                ipn.disable_member(
                    email=member.id,
                    product_id=member.getProperty('product_id'),
                    trans_type='cronjob',
                )
