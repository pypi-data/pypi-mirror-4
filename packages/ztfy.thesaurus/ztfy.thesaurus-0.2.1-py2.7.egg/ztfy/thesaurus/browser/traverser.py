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
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusExtracts

# import local interfaces
from zope.component import getUtility

# import Zope3 packages
from zope.traversing.namespace import view

# import local packages


class ThesaurusManagerNamespaceTraverser(view):
    """++thesaurus++ namespace traverser"""

    def traverse(self, name, ignored):
        return getUtility(IThesaurus, name)


class ThesaurusExtractsNamespaceTraverser(view):
    """++extracts++ namespace traverser"""

    def traverse(self, name, ignored):
        return IThesaurusExtracts(IThesaurus(self.context))


class ThesaurusTermsNamespaceTraverser(view):
    """++terms++ namespace traverser"""

    def traverse(self, name, ignored):
        return IThesaurus(self.context).terms


class ThesaurusCatalogNamespaceTraverser(view):
    """++catalog++ namespace traverser"""

    def traverse(self, name, ignored):
        return IThesaurus(self.context).catalog
