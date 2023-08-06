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

# import local interfaces
from ztfy.thesaurus.interfaces.term import STATUS_ARCHIVED
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus

# import Zope3 packages
from z3c.jsonrpc.publisher import MethodPublisher
from zope.component import queryUtility

# import local packages


class ThesaurusTermsSearchView(MethodPublisher):
    """Thesaurus terms search view"""

    def findTerms(self, query, thesaurus_name='', extract_name='',
                  autoexpand='on_miss', glob='end', limit=20):
        allow_archives = True
        if IThesaurus.providedBy(self.context):
            thesaurus = self.context
        else:
            thesaurus = queryUtility(IThesaurus, thesaurus_name)
            if thesaurus is None:
                return []
            allow_archives = False
        return [ { 'value': term.caption,
                   'caption': term.caption }
                 for term in thesaurus.findTerms(query, extract_name, autoexpand, glob, limit)
                          if allow_archives or (term.status != STATUS_ARCHIVED) ]

    def findTermsWithLabel(self, query, thesaurus_name='', extract_name='',
                           autoexpand='on_miss', glob='end', limit=20):
        allow_archives = True
        if IThesaurus.providedBy(self.context):
            thesaurus = self.context
        else:
            thesaurus = queryUtility(IThesaurus, thesaurus_name)
            if thesaurus is None:
                return []
            allow_archives = False
        return [ { 'value': term.label,
                   'caption': term.label }
                 for term in thesaurus.findTerms(query, extract_name, autoexpand, glob, limit)
                          if allow_archives or (term.status != STATUS_ARCHIVED) ]
