##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id:$
"""

import zope.interface


class ISecurityAware(zope.interface.Interface):
    """Security aware mixin."""

    principalPermissionManager = zope.interface.Attribute(
        """Principal Permission Manager""")
    principalRoleManager = zope.interface.Attribute(
        """Principal Role Manager""")
    rolePermissionManager = zope.interface.Attribute(
        """Role Permission Manager""")
