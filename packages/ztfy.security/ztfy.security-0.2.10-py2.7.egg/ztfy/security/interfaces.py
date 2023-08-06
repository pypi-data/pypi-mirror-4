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

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema import Tuple, TextLine

# import local packages

from ztfy.security import _


class IBaseRoleEvent(IObjectModifiedEvent):
    """Base interface for roles events"""

    principal = Attribute(_("Name of the principal who received the new role"))

    role = Attribute(_("The role who was granted"))


class IGrantedRoleEvent(IBaseRoleEvent):
    """Event interface notified when a role is granted"""


class IRevokedRoleEvent(IBaseRoleEvent):
    """Event interface notified when a role is revoked"""


class ILocalRoleManager(Interface):
    """This interface is used to define classes which can handle local roles"""

    __roles__ = Tuple(title=_("Local roles"),
                      description=_("List of roles IDs handled by local context"),
                      required=True,
                      readonly=True,
                      value_type=TextLine(title=_("Role ID")))


class ILocalRoleIndexer(Interface):
    """This interface is used to help indexing of local roles"""

    def __getattr__(self, name):
        """Get list of principal IDs with granted role name"""


class SecurityManagerException(Exception):
    """Security manager exception"""


class ISecurityManagerRoleChecker(Interface):
    """Security manager role checker"""

    def canGrantRole(role, principal):
        """Return True is role can be granted to principal"""

    def canRevokeRole(role, principal):
        """Return True is role can be revoked from principal"""


class ISecurityManagerBase(Interface):
    """Untrusted security manager interface"""

    def canUsePermission(permission):
        """Return true or false to specify permission usage for given principal"""

    def canView():
        """Return true or false if 'zope.View' permission is granted to given principal"""


class ISecurityManagerReader(Interface):
    """Wrapper interface around Zope3 security roles and permissions"""

    def getLocalRoles(principal=None):
        """Get principal allowed and denied roles on current object

        Result is given as a dictionary :
        { 'allow': ['role1','role2'], 'deny': ['role3',] }
        """

    def getLocalAllowedRoles(principal=None):
        """Get list of locally allowed roles"""

    def getLocalDeniedRoles(principal=None):
        """Get list of locally denied roles"""

    def getRoles(principal=None):
        """Get list of roles, including inherited ones
        
        Result is given as a dictionary :
        { 'allow': ['role1','role2'], 'deny': ['role3',] }
        """

    def getAllowedRoles(principal=None):
        """Get list of allowed roles, including inherited ones"""

    def getDeniedRoles(principal=None):
        """Get list of denied roles, including inherited ones"""

    def getLocalPrincipals(role):
        """Get list of principals with locally defined role
        
        Result is given as a dictionary :
        { 'allow': ['principal1','principal2'], 'deny': ['principal3',] }
        """

    def getLocalAllowedPrincipals(role):
        """Get list of principals with locally granted role"""

    def getLocalDeniedPrincipals(role):
        """Get list of principals with locally denied role"""

    def getPrincipals(role):
        """Get list of principals with access defined for allowed role, including inherited ones
        
        Result is given as a dictionary :
        { 'allow': ['principal1','principal2'], 'deny': ['principal3',] }
        """

    def getAllowedPrincipals(role):
        """Get list of principals with granted access to specified role, including inherited ones"""

    def getDeniedPrincipals(role):
        """Get list of principals with denied access to specified role, including inherited ones"""

    def canUseRole(role, principal=None):
        """Return true or false to specify role usage for given principal"""


class ISecurityManagerWriter(Interface):
    """Wrapper interface around Zope3 security affectations"""

    def grantPermission(permission, principal):
        """Grant given permission to the principal"""

    def grantRole(role, principal, notify=True):
        """Grant given role to the principal"""

    def unsetPermission(permission, principal):
        """Revoke given permission to the principal, falling back to normal acquisition"""

    def unsetRole(role, principal, notify=True):
        """Revoke given role to the principal, falling back to normal acquisition"""

    def denyPermission(permission, principal):
        """Forbid usage of the given permission to the principal, ignoring acquisition"""

    def revokeRole(role, principal, notify=True):
        """Forbid usage of the given role to the principal, ignoring acquisition"""


class ISecurityManager(ISecurityManagerBase, ISecurityManagerReader, ISecurityManagerWriter):
    """Marker interface for security management wrapper"""


class IAuthenticatorSearchAdapter(Interface):
    """Common search adapter for authenticators"""

    def search(query):
        """Get principals matching search query"""
