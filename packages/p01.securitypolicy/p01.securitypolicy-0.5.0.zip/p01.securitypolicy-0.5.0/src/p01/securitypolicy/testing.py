###############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""

import zope.component
import zope.component.testing

from zope.securitypolicy.interfaces import IGrantInfo
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.securitypolicy.interfaces import IRolePermissionManager

from p01.securitypolicy import interfaces
from p01.securitypolicy import securitypolicy


# security policy testing setup
def setUpSecurityPolicyAdapters():
    zope.component.provideAdapter(securitypolicy.PrincipalPermissionManager,
        (interfaces.ISecurityAware,), IPrincipalPermissionManager)
    zope.component.provideAdapter(securitypolicy.PrincipalRoleManager,
        (interfaces.ISecurityAware,), IPrincipalRoleManager)
    zope.component.provideAdapter(securitypolicy.RolePermissionManager,
        (interfaces.ISecurityAware,), IRolePermissionManager)
    zope.component.provideAdapter(securitypolicy.GrantInfoAdapter,
        (interfaces.ISecurityAware,), IGrantInfo)


def setUpSecurityPolicy(test):
    zope.component.testing.setUp()
    setUpSecurityPolicyAdapters()


def tearDownSecurityPolicy(test):
    zope.component.testing.tearDown()
