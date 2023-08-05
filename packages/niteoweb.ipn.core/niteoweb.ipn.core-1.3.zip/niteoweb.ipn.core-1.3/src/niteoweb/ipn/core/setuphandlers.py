# -*- coding: utf-8 -*-
"""Custom import step for niteoweb.ipn.core."""

from plone import api
from niteoweb.ipn.core import VALIDITY
from niteoweb.ipn.core import DISABLED


def setupVarious(context):
    """Custom Python code ran when installing niteoweb.ipn.core.

    @param context:
        Products.GenericSetup.context.DirectoryImportContext instance
    """

    # We check from our GenericSetup context whether we are running
    # add-on installation for your product or any other product
    if context.readDataFile('niteoweb.ipn.core.marker.txt') is None:
        # Not your add-on
        return  # pragma: no cover

    # add timeout field to group properties
    groupdata = api.portal.get_tool('portal_groupdata')
    if not groupdata.hasProperty(VALIDITY):
        groupdata.manage_addProperty(VALIDITY, -1, 'int')

    # add Disabled group
    api.group.create(groupname=DISABLED)
