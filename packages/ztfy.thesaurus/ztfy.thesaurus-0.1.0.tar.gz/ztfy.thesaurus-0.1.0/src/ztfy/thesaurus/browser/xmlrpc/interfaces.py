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

# import Zope3 packages
from zope.interface import Interface

# import local packages


class IThesaurusTargetInfosReader(Interface):
    """Thesaurus target infos"""

    def getThesaurusList(self):
        """Get list of registered thesauri"""

    def getThesaurusInfo(self, thesaurus):
        """Get informations about a given thesaurus"""

    def search(self, query, extract=None, autoexpand='on_miss', glob='end', thesaurus=None):
        """Get a list of terms matching given query several thesauri
        
        @param query: the text search
        @param autoexpand: can be 'off', 'always' or 'on_miss' (default)
        @param glob: can be 'start', 'end' (default), 'both' or None
        @param thesaurus: list of thesauri to search for, or all if None (default)
        """


class IThesaurusReader(Interface):
    """Thesaurus reader interfaces"""

    def search(self, query, autoexpand='on_miss', glob='end'):
        """Get a list of terms matching given query"""

    def getTermInfo(self, term):
        """Get properties of the given term"""
