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
from z3c.form.interfaces import ITextWidget

# import local interfaces
from ztfy.security.schema import IPrincipal

# import Zope3 packages
from zope.interface import Attribute
from zope.schema import Object, List

# import local packages

from ztfy.security import _


class IPrincipalWidget(ITextWidget):
    """Principal widget interface"""

    query_name = Attribute(_("JSON search query method name"))

    auth_plugins = Attribute(_("Selected authentication plug-ins"))

    principal = Object(title=_("Principal"),
                       schema=IPrincipal)

    principal_map = Attribute(_("Principal map"))


class IPrincipalListWidget(ITextWidget):
    """Principal list widget interface"""

    query_name = Attribute(_("JSON search query method name"))

    auth_plugins = Attribute(_("Selected authentication plug-ins"))

    principals = List(title=_("Principals"),
                      value_type=Object(schema=IPrincipal))

    principals_map = Attribute(_("Principals map"))
