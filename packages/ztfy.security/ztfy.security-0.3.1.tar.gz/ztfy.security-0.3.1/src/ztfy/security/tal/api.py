### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from zope.tales.interfaces import ITALESFunctionNamespace

# import local interfaces
from ztfy.security.tal.interfaces import ISecurityPermissionTalesAPI

# import Zope3 packages
from zope.interface import implements

# import local packages
from ztfy.security.security import getSecurityManager


class SecurityPermissionTalesAdapter(object):
    """Security permission TALES adapter"""

    implements(ISecurityPermissionTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context
        self.sm = getSecurityManager(context)

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def __getattr__(self, permission):
        if self.sm is None:
            return False
        return self.sm.canUsePermission(permission)
