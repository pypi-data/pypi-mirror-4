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
from zope.schema.interfaces import IField
from zope.security.interfaces import IPrincipal

# import local interfaces
from ztfy.security.interfaces import ISecurityManager

# import Zope3 packages

# import local packages

from ztfy.security import _


class RolePrincipalsProperty(object):
    """Principals list property matching local role owners"""

    def __init__(self, field, role, name=None, output=str, **args):
        if not IField.providedBy(field):
            raise ValueError, _("Provided field must implement IField interface...")
        if output not in (str, list):
            raise ValueError, _("Field output must be 'list' or 'str' types")
        if name is None:
            name = field.__name__
        self.__field = field
        self.__name = name
        self.__role = role
        self.__output = output
        self.__args = args

    def __get__(self, instance, klass):
        if instance is None:
            return self
        sm = ISecurityManager(instance, None)
        if sm is None:
            result = []
        else:
            result = sm.getLocalAllowedPrincipals(self.__role)
        if self.__output is str:
            return ','.join(result)
        else:
            return result

    def __set__(self, instance, value):
        if value is None:
            value = []
        elif isinstance(value, (str, unicode)):
            value = value.split(',')
        for i, v in enumerate(value):
            if IPrincipal.providedBy(v):
                value[i] = v.id
        field = self.__field.bind(instance)
        field.validate(value)
        if field.readonly:
            raise ValueError(self.__name, _("Field is readonly"))
        sm = ISecurityManager(instance, None)
        principals = sm.getLocalAllowedPrincipals(self.__role)
        removed = set(principals) - set(value)
        added = set(value) - set(principals)
        for principal in removed:
            sm.unsetRole(self.__role, principal)
        for principal in added:
            sm.grantRole(self.__role, principal)
