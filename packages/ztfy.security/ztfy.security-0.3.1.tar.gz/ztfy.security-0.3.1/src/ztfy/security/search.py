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
from zope.authentication.interfaces import IAuthentication, PrincipalLookupError
from zope.pluggableauth.interfaces import IPrincipalInfo
from zope.pluggableauth.plugins.groupfolder import IGroupFolder
from zope.pluggableauth.plugins.principalfolder import IInternalPrincipalContainer

# import local interfaces
from ztfy.security.interfaces import IAuthenticatorSearchAdapter

# import Zope3 packages
from zope.component import adapts, queryUtility
from zope.i18n import translate
from zope.interface import implements

# import local packages
from ztfy.utils.request import getRequest, getRequestData, setRequestData

from ztfy.security import _


class NoPrincipal(object):

    implements(IPrincipalInfo)

    def __init__(self):
        self.id = ''

    title = _("No selected principal")
    description = _("No principal was selected")


class MissingPrincipal(object):

    implements(IPrincipalInfo)

    def __init__(self, uid):
        self.id = uid
        self.request = getRequest()

    @property
    def title(self):
        return translate(_("< missing principal %s >"), context=self.request) % self.id

    @property
    def description(self):
        return translate(_("This principal can't be found in any authentication utility..."), context=self.request)


class PrincipalFolderSearchAdapter(object):
    """Principal folder search adapter"""

    adapts(IInternalPrincipalContainer)
    implements(IAuthenticatorSearchAdapter)

    def __init__(self, context):
        self.context = context

    def search(self, query):
        return self.context.search({ 'search': query })


class GroupFolderSearchAdapter(object):
    """Principal group search adapter"""

    adapts(IGroupFolder)
    implements(IAuthenticatorSearchAdapter)

    def __init__(self, context):
        self.context = context

    def search(self, query):
        return self.context.search({ 'search': query })


REQUEST_PRINCIPALS_KEY = 'ztfy.security.principals.cache'

def getPrincipal(uid, auth=None, request=None):
    """Get a principal"""
    if not uid:
        return NoPrincipal()
    if request is not None:
        cache = getRequestData(REQUEST_PRINCIPALS_KEY, request, None)
        if cache and (uid in cache):
            return cache[uid]
    if auth is None:
        auth = queryUtility(IAuthentication)
    if auth is None:
        return NoPrincipal()
    try:
        result = auth.getPrincipal(uid)
    except PrincipalLookupError:
        return MissingPrincipal(uid)
    else:
        if request is not None:
            cache = cache or {}
            cache[uid] = result
            setRequestData(REQUEST_PRINCIPALS_KEY, cache, request)
        return result


def findPrincipals(query, names=None):
    """Search for principals"""
    query = query.strip()
    if not query:
        return ()
    auth = queryUtility(IAuthentication)
    if auth is None:
        return ()
    if isinstance(names, (str, unicode)):
        names = names.split(',')
    result = []
    for name, plugin in auth.getQueriables():
        if (not names) or (name in names):
            search = IAuthenticatorSearchAdapter(plugin.authplugin, None)
            if search is not None:
                result.extend([getPrincipal(uid, auth) for uid in search.search(query)])
    return sorted(result, key=lambda x: x.title)
