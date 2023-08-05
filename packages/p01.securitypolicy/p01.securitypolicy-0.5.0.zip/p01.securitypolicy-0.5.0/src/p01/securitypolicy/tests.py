###############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""

import doctest
import unittest
from zope.securitypolicy.tests.test_securitymap import TestSecurityMap

from p01.securitypolicy import testing
from p01.securitypolicy import securitypolicy

# securitypolicy
class TestPrincipalPermissionManager(TestSecurityMap):

    def _getSecurityMap(self):
        obj = securitypolicy.SecurityAware()
        return securitypolicy.PrincipalPermissionManager(obj)


class TestPrincipalRoleManager(TestSecurityMap):

    def _getSecurityMap(self):
        obj = securitypolicy.SecurityAware()
        return securitypolicy.PrincipalRoleManager(obj)


class TestRolePermissionManager(TestSecurityMap):

    def _getSecurityMap(self):
        obj = securitypolicy.SecurityAware()
        return securitypolicy.RolePermissionManager(obj)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            package='p01.securitypolicy',
            setUp=testing.setUpSecurityPolicy,
            tearDown=testing.tearDownSecurityPolicy,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        unittest.makeSuite(TestPrincipalPermissionManager),
        unittest.makeSuite(TestPrincipalRoleManager),
        unittest.makeSuite(TestRolePermissionManager),
        ))


if __name__ == '__main__':
    unittest.main()