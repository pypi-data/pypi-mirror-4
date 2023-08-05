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
from hurry.query.interfaces import IQuery
from zope.authentication.interfaces import IAuthentication

# import local interfaces
from ztfy.security.interfaces import IGrantedRoleEvent, IRevokedRoleEvent

# import Zope3 packages
from hurry.query.set import AnyOf
from zope.component import adapter, getUtility, getUtilitiesFor

# import local packages
from ztfy.security.indexer import ALL_ROLES_INDEX_NAME


@adapter(IGrantedRoleEvent)
def handleGrantedOperatorRole(event):
    if event.role in ('ztfy.ThesaurusManager', 'ztfy.ThesaurusContentManager', 'ztfy.ThesaurusExtractManager'):
        for _name, auth in getUtilitiesFor(IAuthentication):
            operators = auth.get('groups', {}).get('operators', None)
            if operators and (event.principal not in operators.principals):
                operators.principals = operators.principals + (event.principal,)


@adapter(IRevokedRoleEvent)
def handleRevokedOperatorRole(event):
    if event.role in ('ztfy.ThesaurusManager', 'ztfy.ThesaurusContentManager', 'ztfy.ThesaurusExtractManager'):
        query = getUtility(IQuery)
        objects = query.searchResults(AnyOf(('SecurityCatalog', ALL_ROLES_INDEX_NAME),
                                            (event.principal,)))
        if (not objects) or ((len(objects) == 1) and (event.object in objects)):
            for _name, auth in getUtilitiesFor(IAuthentication):
                operators = auth.get('groups', {}).get('operators', None)
                if (operators is not None) and (event.principal in operators.principals):
                    principals = list(operators.principals)
                    principals.remove(event.principal)
                    operators.principals = tuple(principals)
