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
from z3c.form.interfaces import IFieldWidget
from zope.schema.interfaces import IField

# import local interfaces
from ztfy.security.browser.widget.interfaces import IPrincipalWidget, IPrincipalListWidget
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form.browser.text import TextWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer, implementsOnly

# import local packages
from ztfy.jqueryui import jquery_multiselect
from ztfy.security.search import getPrincipal


class PrincipalWidget(TextWidget):
    """Principal widget"""

    implementsOnly(IPrincipalWidget)

    query_name = 'findPrincipals'
    auth_plugins = ()

    @property
    def principal(self):
        return getPrincipal(self.value)

    @property
    def principal_map(self):
        if not self.value:
            return u''
        principal = self.principal
        if principal is None:
            return ''
        return "{ '%s': '%s' }" % (principal.id,
                                   principal.title.replace("'", "&#039;"))

    @property
    def auth_plugins_value(self):
        return (";;{'names':'%s'}" % ','.join(self.auth_plugins)) if self.auth_plugins else ''

    def render(self):
        jquery_multiselect.need()
        return super(PrincipalWidget, self).render()


@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def PrincipalFieldWidget(field, request):
    """IPrincipalWidget factory for Principal fields"""
    return FieldWidget(field, PrincipalWidget(request))


class PrincipalListWidget(TextWidget):
    """Principals list widget"""

    implementsOnly(IPrincipalListWidget)

    query_name = 'findPrincipals'
    auth_plugins = ()

    @property
    def principals(self):
        if not hasattr(self, '_v_principals'):
            self._v_principals = sorted((getPrincipal(v) for v in self.value.split(',')), key=lambda x: x.title)
        return self._v_principals

    @property
    def principals_map(self):
        return '{ %s }' % ',\n'.join(("'%s': '%s'" % (principal.id, principal.title.replace("'", "&#039;"))
                                      for principal in self.principals))

    @property
    def auth_plugins_value(self):
        return (";;{'names':'%s'}" % ','.join(self.auth_plugins)) if self.auth_plugins else ''

    def render(self):
        jquery_multiselect.need()
        return super(PrincipalListWidget, self).render()


@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def PrincipalListFieldWidget(field, request):
    """IPrincipalListWidget factory for PrincipalList fields"""
    return FieldWidget(field, PrincipalListWidget(request))
