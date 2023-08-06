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

# import local interfaces
from ztfy.jqueryui import jquery_multiselect

# import Zope3 packages
from z3c.form import button, field
from z3c.formjs import jsaction
from zope.interface import Interface

# import local packages
from ztfy.skin.form import DialogEditForm

from ztfy.security import _


class IEditFormButtons(Interface):
    """Default edit form buttons"""

    submit = button.Button(title=_("Submit"))
    reset = jsaction.JSButton(title=_("Reset"))


class RolesEditForm(DialogEditForm):
    """Roles edit form"""

    legend = _("Define roles on current context")

    interfaces = ()
    resources = (jquery_multiselect,)

    @property
    def fields(self):
        return field.Fields(*self.interfaces)
