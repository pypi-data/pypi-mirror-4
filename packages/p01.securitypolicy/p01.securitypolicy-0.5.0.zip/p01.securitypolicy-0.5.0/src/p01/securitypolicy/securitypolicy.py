###############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
from zope.security.proxy import removeSecurityProxy
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.interfaces import IRolePermissionManager
from zope.securitypolicy.interfaces import IGrantInfo
from zope.securitypolicy.interfaces import Allow
from zope.securitypolicy.interfaces import Deny
from zope.securitypolicy.interfaces import Unset
from zope.securitypolicy import securitymap

from p01.securitypolicy import interfaces


class SecurityAware(object):
    """Security map mixin."""

    zope.interface.implements(interfaces.ISecurityAware)

    principalPermissionManager = None
    principalRoleManager = None
    rolePermissionManager = None

    def __init__(self):
        self.setUpSecurity()

    def setUpSecurity(self):
        if self.principalPermissionManager is None:
            self.principalPermissionManager = securitymap.PersistentSecurityMap()
        if self.principalRoleManager is None:
            self.principalRoleManager = securitymap.PersistentSecurityMap()
        if self.rolePermissionManager is None:
            self.rolePermissionManager = securitymap.PersistentSecurityMap()


class SecurityManager(securitymap.SecurityMap):
    """SecurityManagerAdapter"""

    zope.component.adapts(interfaces.ISecurityAware)

    def addCell(self, rowentry, colentry, value):
        self.map.addCell(rowentry, colentry, value)

    def delCell(self, rowentry, colentry):
        self.map.delCell(rowentry, colentry)


class PrincipalPermissionManager(SecurityManager):
    """Mappings between principals and permissions."""

    zope.interface.implements(IPrincipalPermissionManager)

    def __init__(self, context):
        self.__parent__ = context
        self.context = context
        self.map = self.context.principalPermissionManager
        self._byrow = self.map._byrow
        self._bycol = self.map._bycol

    def grantPermissionToPrincipal(self, permission_id, principal_id):
        self.map.addCell(permission_id, principal_id, Allow)

    def denyPermissionToPrincipal(self, permission_id, principal_id):
        self.map.addCell(permission_id, principal_id, Deny)

    unsetPermissionForPrincipal = SecurityManager.delCell
    getPrincipalsForPermission = SecurityManager.getRow
    getPermissionsForPrincipal = SecurityManager.getCol

    def getSetting(self, permission_id, principal_id, default=Unset):
        return self.map.queryCell(permission_id, principal_id,
            default)
       
    getPrincipalsAndPermissions = SecurityManager.getAllCells


class PrincipalRoleManager(SecurityManager):
    """Mappings between principals and roles."""

    zope.interface.implements(IPrincipalRoleManager)

    def __init__(self, context):
        self.__parent__ = context
        self.context = context
        self.map = self.context.principalRoleManager
        self._byrow = self.map._byrow
        self._bycol = self.map._bycol

    def assignRoleToPrincipal(self, role_id, principal_id):
        self.map.addCell(role_id, principal_id, Allow)

    def removeRoleFromPrincipal(self, role_id, principal_id):
        self.map.addCell(role_id, principal_id, Deny)

    unsetRoleForPrincipal = SecurityManager.delCell
    getPrincipalsForRole = SecurityManager.getRow
    getRolesForPrincipal = SecurityManager.getCol
    
    def getSetting(self, role_id, principal_id):
        return self.map.queryCell(role_id, principal_id, default=Unset)

    getPrincipalsAndRoles = SecurityManager.getAllCells


class RolePermissionManager(SecurityManager):
    """Provide adapter that manages role permission data in an object attribute
    """

    zope.interface.implements(IRolePermissionManager)

    def __init__(self, context):
        self.__parent__ = context
        self.context = context
        self.map = self.context.rolePermissionManager
        self._byrow = self.map._byrow
        self._bycol = self.map._bycol

    def grantPermissionToRole(self, permission_id, role_id):
        self.map.addCell(permission_id, role_id, Allow)

    def denyPermissionToRole(self, permission_id, role_id):
        self.map.addCell(permission_id, role_id, Deny)

    unsetPermissionFromRole = SecurityManager.delCell
    getRolesForPermission = SecurityManager.getRow
    getPermissionsForRole = SecurityManager.getCol
    getRolesAndPermissions = SecurityManager.getAllCells

    def getSetting(self, permission_id, role_id):
        return self.map.queryCell(permission_id, role_id, default=Unset)


class GrantInfoAdapter(object):
    """Grant info adapter."""

    zope.interface.implements(IGrantInfo)
    zope.component.adapts(interfaces.ISecurityAware)

    prinper = {}
    prinrole = {}
    permrole = {}

    def __init__(self, context):
        self.context = removeSecurityProxy(context)
        self.prinper = self.context.principalPermissionManager._bycol
        self.prinrole = self.context.principalRoleManager._bycol
        self.permrole = self.context.rolePermissionManager._byrow
            
    def __nonzero__(self):
        return bool(self.prinper or self.prinrole or self.permrole)

    def principalPermissionGrant(self, principal, permission):
        prinper = self.prinper.get(principal)
        if prinper:
            return prinper.get(permission, Unset)
        return Unset

    def getRolesForPermission(self, permission):
        permrole = self.permrole.get(permission)
        if permrole:
            return permrole.items()
        return ()

    def getRolesForPrincipal(self, principal):
        prinrole = self.prinrole.get(principal)
        if prinrole:
            return prinrole.items()
        return ()
