### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotatable

# import local interfaces
from ztfy.security.interfaces import ILocalRoleManager, ISecurityManager, ILocalRoleIndexer

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements
from zope.security.checker import CheckerPublic
from zope.security.proxy import removeSecurityProxy

# import local packages


ALL_ROLES_INDEX_NAME = 'all_roles'


class LocalRoleIndexer(object):
    """Local role indexer helper interface"""

    adapts(IAnnotatable)
    implements(ILocalRoleIndexer)

    def __init__(self, context):
        self.context = context

    __Security_checker__ = CheckerPublic

    def __getattr__(self, name):
        result = set()
        sm = ISecurityManager(self.context, None)
        if sm is None:
            return result
        if name == ALL_ROLES_INDEX_NAME:
            manager = ILocalRoleManager(self.context, None)
            if manager is None:
                return result
            names = manager.__roles__
        else:
            names = (name,)
        for name in names:
            result |= removeSecurityProxy(sm.getLocalAllowedPrincipals(name))
        return result
