# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('niteoweb.ipn.core')

VALIDITY = 'validity'
"""Name of a group property that contains number of days of validity for
members in that group."""

DISABLED = 'disabled'
"""Groupname of group containing disabled members."""

PGI = 'ipn_%s'
"""Product Group ID, for calculating id of product group out of product id."""


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
