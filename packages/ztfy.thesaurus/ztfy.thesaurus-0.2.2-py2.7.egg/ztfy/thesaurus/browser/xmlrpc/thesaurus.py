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
from ztfy.thesaurus.browser.xmlrpc.interfaces import IThesaurusTargetInfosReader
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus

# import Zope3 packages
from zope.component import queryUtility
from zope.interface import implements
from zope.publisher.xmlrpc import XMLRPCView
from zope.schema.interfaces import IVocabularyFactory
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.utils.date import unidate, datetodatetime


class XMLRPCThesaurusTargetView(XMLRPCView):
    """Thesaurus target XML-RPC view"""

    implements(IThesaurusTargetInfosReader)

    def getThesaurusList(self):
        factory = queryUtility(IVocabularyFactory, 'ZTFY thesaurus')
        if factory is not None:
            vocabulary = factory(self.context)
            return [{ 'name': term.token,
                      'url': absoluteURL(term.value, self.request) } for term in vocabulary]

    def getThesaurusInfo(self, thesaurus):
        thesaurus = queryUtility(IThesaurus, thesaurus)
        if thesaurus is not None:
            return { 'name': thesaurus.name,
                     'title': thesaurus.title,
                     'subject': thesaurus.subject,
                     'description': thesaurus.description,
                     'language': thesaurus.language,
                     'creator': thesaurus.creator,
                     'publisher': thesaurus.publisher,
                     'created': thesaurus.created and unidate(datetodatetime(thesaurus.created)) or None,
                     'length': len(thesaurus.terms),
                     'top_terms': [term.label for term in thesaurus.top_terms],
                     'url': absoluteURL(thesaurus, self.request) }

    def search(self, query, extract=None, autoexpand='on_miss', glob='end', thesaurus=None):
        if thesaurus:
            thesaurus_list = [ queryUtility(IThesaurus, name) for name in thesaurus ]
        else:
            factory = queryUtility(IVocabularyFactory, 'ZTFY thesaurus')
            if factory is not None:
                vocabulary = factory(self.context)
                thesaurus_list = [ term.value for term in vocabulary ]
            else:
                thesaurus_list = []
        result = []
        if thesaurus_list:
            for thesaurus in thesaurus_list:
                name = thesaurus.name
                result.extend([ { 'thesaurus': name,
                                  'label': term.label } for term in thesaurus.findTerms(query, extract, autoexpand, glob) ])
        return result


class XMLRPCThesaurusView(XMLRPCView):
    """Thesaurus XML-RPC views"""

    def search(self, query, extract=None, autoexpand='on_miss', glob='end'):
        thesaurus = IThesaurus(self.context)
        return [ term.label for term in thesaurus.findTerms(query, extract, autoexpand, glob) ]

    def getTermInfo(self, term):
        term = IThesaurus(self.context).terms.get(term)
        if term is not None:
            return { 'label': term.label,
                     'definition': term.definition,
                     'note': term.note,
                     'generic': term.generic and term.generic.label or None,
                     'specifics': [specific.label for specific in term.specifics],
                     'associations': [association.label for association in term.associations],
                     'usage': term.usage and term.usage.label or None,
                     'used_for': [used.label for used in term.used_for],
                     'status': term.status,
                     'level': term.level,
                     'created': unidate(term.created),
                     'modified': unidate(term.modified),
                     'url': absoluteURL(term, self.request) }


class XMLRPCThesaurusTermView(XMLRPCView):
    """Thesaurus term XML-RPC views"""
