### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotatable
from zope.security.interfaces import IPermission, IPrincipal
from zope.securitypolicy.interfaces import IRole, IPrincipalRoleManager, IPrincipalPermissionManager

# import local interfaces
from ztfy.security.interfaces import ILocalRoleManager, ISecurityManager, ISecurityManagerRoleChecker, \
                                     IBaseRoleEvent, IGrantedRoleEvent, IRevokedRoleEvent

# import Zope3 packages
from zope.component import adapts
import zope.event
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent
from zope.security.management import checkPermission
from zope.traversing.api import getParent

# import local packages
from ztfy.security.interfaces import SecurityManagerException
from ztfy.utils import request

from ztfy.security import _


class BaseRoleEvent(ObjectModifiedEvent):

    implements(IBaseRoleEvent)

    def __init__(self, object, principal, role):
        super(BaseRoleEvent, self).__init__(object)
        self.principal = principal
        self.role = role


class GrantedRoleEvent(BaseRoleEvent):

    implements(IGrantedRoleEvent)


class RevokedRoleEvent(BaseRoleEvent):

    implements(IRevokedRoleEvent)


class SecurityManagerAdapter(object):

    adapts(IAnnotatable)
    implements(ISecurityManager)

    def __init__(self, context):
        self.context = context

    # ISecurityManagerBase methods
    def canUsePermission(self, permission):
        if IPermission.providedBy(permission):
            permission = IPermission(permission).id
        try:
            return checkPermission(permission, self.context)
        except:
            return False

    def canView(self):
        return self.canUsePermission('zope.View')

    # ISecurityManagerReader methods
    def getLocalRoles(self, principal=None):
        if principal is None:
            principal = request.getPrincipal()
        if not principal:
            return None
        if IPrincipal.providedBy(principal):
            principal = IPrincipal(principal).id
        manager = IPrincipalRoleManager(self.context)
        roles = manager.getRolesForPrincipal(principal)
        return { 'allow': set((role[0] for role in roles if role[1].getName() == 'Allow')),
                 'deny':  set((role[0] for role in roles if role[1].getName() == 'Deny')) }

    def getLocalAllowedRoles(self, principal=None):
        roles = self.getLocalRoles(principal)
        if not roles:
            return None
        return roles['allow']

    def getLocalDeniedRoles(self, principal=None):
        roles = self.getLocalRoles(principal)
        if not roles:
            return None
        return roles['deny']

    def getRoles(self, principal=None):
        result = { 'allow': set(),
                   'deny':  set() }
        context = self.context
        while context is not None:
            roles = ISecurityManager(context).getLocalRoles(principal)
            if roles:
                for role in roles['allow']:
                    if role not in result['deny']:
                        result['allow'].add(role)
                for role in roles['deny']:
                    if role not in result['allow']:
                        result['deny'].add(role)
            context = getParent(context)
        return result

    def getAllowedRoles(self, principal=None):
        return self.getRoles(principal)['allow']

    def getDeniedRoles(self, principal=None):
        return self.getRoles(principal)['deny']

    def getLocalPrincipals(self, role):
        if IRole.providedBy(role):
            role = IRole(role).id
        manager = IPrincipalRoleManager(self.context)
        principals = manager.getPrincipalsForRole(role)
        return { 'allow': set((principal[0] for principal in principals if principal[1].getName() == 'Allow')),
                 'deny':  set((principal[0] for principal in principals if principal[1].getName() == 'Deny')) }

    def getLocalAllowedPrincipals(self, role):
        return self.getLocalPrincipals(role)['allow']

    def getLocalDeniedPrincipals(self, role):
        return self.getLocalPrincipals(role)['deny']

    def getPrincipals(self, role):
        result = { 'allow': set(),
                   'deny':  set() }
        context = self.context
        while context is not None:
            principals = ISecurityManager(context).getLocalPrincipals(role)
            for principal in principals['allow']:
                if principal not in result['deny']:
                    result['allow'].add(principal)
            for principal in principals['deny']:
                if principal not in result['allow']:
                    result['deny'].add(principal)
            context = getParent(context)
        return result

    def getAllowedPrincipals(self, role):
        return self.getPrincipals(role)['allow']

    def getDeniedPrincipals(self, role):
        return self.getPrincipals(role)['deny']

    def canUseRole(self, role, principal=None):
        if IRole.providedBy(role):
            role = IRole(role).id
        if principal is None:
            principal = request.getPrincipal()
        if IPrincipal.providedBy(principal):
            principal = principal.id
        if principal == 'zope.manager':
            return True
        return role in self.getAllowedRoles(principal)

    # ISecurityManagerWriter methods
    def _getLocalRoles(self):
        manager = ILocalRoleManager(self.context, None)
        if manager is None:
            return None
        return manager.__roles__

    def grantPermission(self, permission, principal):
        if IPermission.providedBy(permission):
            permission = IPermission(permission).id
        if IPrincipal.providedBy(principal):
            principal = IPrincipal(principal).id
        ppm = IPrincipalPermissionManager(self.context)
        ppm.grantPermissionToPrincipal(permission, principal)

    def grantRole(self, role, principal, notify=True):
        if IRole.providedBy(role):
            role = IRole(role).id
        if IPrincipal.providedBy(principal):
            principal = IPrincipal(principal).id
        roles = self._getLocalRoles()
        if roles and (role not in roles):
            raise SecurityManagerException, _("The role %s is not handled by this object's class") % role
        checker = ISecurityManagerRoleChecker(self.context, None)
        if (checker is not None) and (not checker.canGrantRole(role, principal)):
            raise SecurityManagerException, _("You are not authorized to grant role %s to principal %s") % (role, principal)
        prm = IPrincipalRoleManager(self.context)
        prm.assignRoleToPrincipal(role, principal)
        if notify:
            zope.event.notify(GrantedRoleEvent(self.context, principal, role))

    def unsetPermission(self, permission, principal):
        if IPermission.providedBy(permission):
            permission = IPermission(permission).id
        if IPrincipal.providedBy(principal):
            principal = IPrincipal(principal).id
        ppm = IPrincipalPermissionManager(self.context)
        ppm.unsetPermissionForPrincipal(permission, principal)

    def unsetRole(self, role, principal, notify=True):
        if IRole.providedBy(role):
            role = IRole(role).id
        if IPrincipal.providedBy(principal):
            principal = IPrincipal(principal).id
        roles = self._getLocalRoles()
        if roles and (role not in roles):
            raise SecurityManagerException, _("The role %s is not handled by this object's class") % role
        checker = ISecurityManagerRoleChecker(self.context, None)
        if (checker is not None) and (not checker.canRevokeRole(role, principal)):
            raise SecurityManagerException, _("You are not authorized to revoke role %s for principal %s") % (role, principal)
        prm = IPrincipalRoleManager(self.context)
        prm.unsetRoleForPrincipal(role, principal)
        if notify:
            zope.event.notify(RevokedRoleEvent(self.context, principal, role))

    def denyPermission(self, permission, principal):
        if IPermission.providedBy(permission):
            permission = IPermission(permission).id
        if IPrincipal.providedBy(principal):
            principal = IPrincipal(principal).id
        ppm = IPrincipalPermissionManager(self.context)
        ppm.denyPermissionToPrincipal(permission, principal)

    def revokeRole(self, role, principal, notify=True):
        if IRole.providedBy(role):
            role = IRole(role).id
        if IPrincipal.providedBy(principal):
            principal = IPrincipal(principal).id
        roles = self._getLocalRoles()
        if roles and (role not in roles):
            raise SecurityManagerException, _("The role %s is not handled by this object's class") % role
        checker = ISecurityManagerRoleChecker(self.context, None)
        if (checker is not None) and (not checker.canRevokeRole(role, principal)):
            raise SecurityManagerException, _("You are not authorized to revoke role %s for principal %s") % (role, principal)
        prm = IPrincipalRoleManager(self.context)
        prm.removeRoleFromPrincipal(role, principal)
        if notify:
            zope.event.notify(RevokedRoleEvent(self.context, principal, role))


def getSecurityManager(context):
    while context is not None:
        sm = ISecurityManager(context, None)
        if sm is not None:
            return sm
        context = getParent(context)
    return None
