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
from persistent import Persistent
import BTrees.Length

# import Zope3 interfaces
from hurry.query.interfaces import IQuery
from zope.annotation.interfaces import IAnnotations
from zope.catalog.interfaces import ICatalog
from zope.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.location.interfaces import ISublocations
from zopyx.txng3.core.interfaces.ting import ITingIndex

# import local interfaces
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus, \
                                                IThesaurusExtractInfo, \
                                                IThesaurusExtracts
from ztfy.thesaurus.interfaces.term import IThesaurusTermsContainer, IThesaurusTerm

# import Zope3 packages
from hurry.query import And
from zope.catalog.catalog import Catalog
from zope.component import adapter, adapts, getUtility, queryUtility, getSiteManager
from zope.container.contained import Contained
from zope.container.folder import Folder
from zope.interface import implementer, implements
from zope.schema.fieldproperty import FieldProperty
from zope.location.location import locate
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getName

# import local packages
from ztfy.utils.catalog import indexObject, unindexObject
from ztfy.utils.catalog.index import TextIndexNG, Text as BaseTextSearch
from ztfy.thesaurus.interfaces.loader import IThesaurusLoader
from ztfy.thesaurus.interfaces.tree import ITree
from ztfy.security.property import RolePrincipalsProperty
from ztfy.utils.traversing import getParent


class ThesaurusIndexSearch(BaseTextSearch):
    """Custom text search index using catalog instance instead of name"""

    def getIndex(self, context=None):
        if ICatalog.providedBy(self.catalog_name):
            catalog = self.catalog_name
        else:
            catalog = getUtility(ICatalog, self.catalog_name, context)
        index = catalog[self.index_name]
        assert ITingIndex.providedBy(index)
        return index


class ThesaurusTermsContainer(Folder):
    """Thesaurus terms container"""

    implements(IThesaurusTermsContainer)

    def __init__(self, *args, **kwargs):
        super(ThesaurusTermsContainer, self).__init__(*args, **kwargs)
        self._length = BTrees.Length.Length()

    def __setitem__(self, name, object):
        if name not in self.data:
            self._length.change(1)
        self.data.__setitem__(name, object)
        locate(object, self, name)
        thesaurus = IThesaurus(self.__parent__, None)
        if thesaurus is not None:
            catalog = thesaurus.catalog
            indexObject(object, catalog)

    def __delitem__(self, name):
        self.data.__delitem__(name)
        self._length.change(-1)
        thesaurus = IThesaurus(self.__parent__, None)
        if thesaurus is not None:
            catalog = thesaurus.catalog
            unindexObject(object, catalog)

    def __len__(self):
        return self._length()

    def iterkeys(self):
        return self.data.iterkeys()

    def itervalues(self):
        return self.data.itervalues()

    def iteritems(self):
        return self.data.iteritems()


class Thesaurus(Persistent, Contained):
    """Thesaurus utility"""

    implements(IThesaurus, ISublocations)

    __roles__ = ('ztfy.ThesaurusManager', 'ztfy.ThesaurusContentManager')

    name = FieldProperty(IThesaurus['name'])
    title = FieldProperty(IThesaurus['title'])
    subject = FieldProperty(IThesaurus['subject'])
    description = FieldProperty(IThesaurus['description'])
    creator = FieldProperty(IThesaurus['creator'])
    publisher = FieldProperty(IThesaurus['publisher'])
    created = FieldProperty(IThesaurus['created'])
    language = FieldProperty(IThesaurus['language'])
    terms = None
    _top_terms = FieldProperty(IThesaurus['top_terms'])
    catalog = FieldProperty(IThesaurus['catalog'])

    administrators = RolePrincipalsProperty(IThesaurus['administrators'], role='ztfy.ThesaurusManager')
    contributors = RolePrincipalsProperty(IThesaurus['contributors'], role='ztfy.ThesaurusContentManager')

    def __init__(self, name=None, description=None, terms=[], top_terms=[]):
        if name:
            self.name = name
        if description:
            self.title = description.title
            self.subject = description.subject
            self.description = description.description
            self.creator = description.creator
            self.publisher = description.publisher
            self.created = description.created
            self.language = description.language
        if not IThesaurusTermsContainer.providedBy(terms):
            terms = ThesaurusTermsContainer(terms)
        self.terms = terms
        locate(terms, self, '++terms++')
        self.resetTermsParent()
        self.resetTopTerms()

    def sublocations(self):
        return (self.terms, self.catalog)

    @property
    def top_terms(self):
        return self._top_terms

    @top_terms.setter
    def top_terms(self, value):
        self._top_terms = [removeSecurityProxy(term) for term in value or ()]

    def initCatalog(self):
        catalog = self.catalog = Catalog()
        locate(catalog, self, '++catalog++')
        index = TextIndexNG('label', IThesaurusTerm,
                            field_callable=False,
                            languages=self.language,
                            storage='txng.storages.term_frequencies',
                            dedicated_storage=False,
                            use_stopwords=True,
                            use_normalizer=True,
                            ranking=True)
        locate(index, catalog, 'label"')
        catalog['label'] = index
        locate(self.terms, self, '++terms++')
        for term in self.terms.itervalues():
            indexObject(term, catalog)

    def delete(self):
        manager = getSiteManager(self)
        manager.unregisterUtility(self, IThesaurus, self.name)
        default = manager['default']
        name = 'Thesaurus::' + self.name
        # reparent thesaurus to site management folder
        locate(self, default, name)
        del default[name]

    def clear(self):
        self.terms.data.clear()
        self.catalog.clear()
        self.top_terms = []

    def load(self, configuration):
        loader = queryUtility(IThesaurusLoader, configuration.format)
        if loader is not None:
            result = loader.load(configuration.data)
            self.merge(configuration, result)

    def merge(self, configuration, thesaurus=None):
        if thesaurus is None:
            loader = queryUtility(IThesaurusLoader, configuration.format)
            if loader is not None:
                thesaurus = loader.load(configuration.data)
        if thesaurus is not None:
            # define or merge items from given thesaurus
            terms = self.terms
            for key, term in thesaurus.terms.iteritems():
                if key in terms:
                    terms[key].merge(term)
                else:
                    terms[key] = term
        self.resetTermsParent()
        self.resetTopTerms()

    def resetTermsParent(self):
        for term in self.terms.itervalues():
            # reset generic/specifics attributes
            generic = term.generic
            if (generic is not None) and (term not in generic.specifics):
                generic.specifics = generic.specifics + [term, ]
            # reset term's first level parent
            parent = term
            while parent.generic is not None:
                parent = parent.generic
            term.parent = parent

    def resetTopTerms(self):
        self.top_terms = [ term for term in self.terms.itervalues()
                           if (not term.generic) and (not term.usage) ]

    def findTerms(self, query=None, extract=None, autoexpand='on_miss', glob='end', limit=None):
        params = []
        start = ''
        end = ''
        if '*' not in query:
            if glob in ('start', 'both'):
                start = u'*'
            if glob in ('end', 'both'):
                end = u'*'
        params.append(ThesaurusIndexSearch((self.catalog, 'label'), { 'query': u' '.join((u'%s%s%s' % (start, m, end) for m in query.split()
                                                                                                                      if len(m) > 2)),
                                                                      'autoexpand': autoexpand,
                                                                      'ranking': True }))
        terms = getUtility(IQuery).searchResults(And(*params), limit=limit)
        if extract:
            terms = [ term for term in terms
                                    if extract in term.extracts ]
        return terms


@adapter(IThesaurus, IObjectAddedEvent)
def handleNewThesaurus(thesaurus, event):
    """Handle new thesaurus"""
    thesaurus.initCatalog()


class ThesaurusTreeAdapter(object):
    """Thesaurus tree adapter"""

    adapts(IThesaurus)
    implements(ITree)

    def __init__(self, context):
        self.context = context

    def getRootNodes(self):
        return self.context.top_terms


#
# Thesaurus extracts
#

class ThesaurusExtract(Persistent, Contained):
    """Thesaurus extract"""

    implements(IThesaurusExtractInfo)

    __roles__ = ('ztfy.ThesaurusExtractManager',)

    name = FieldProperty(IThesaurusExtractInfo['name'])
    description = FieldProperty(IThesaurusExtractInfo['description'])
    abbreviation = FieldProperty(IThesaurusExtractInfo['abbreviation'])
    color = FieldProperty(IThesaurusExtractInfo['color'])

    managers = RolePrincipalsProperty(IThesaurusExtractInfo['managers'], role='ztfy.ThesaurusExtractManager')

    def addTerm(self, term):
        term.addExtract(self)

    def removeTerm(self, term):
        term.removeExtract(self)


@adapter(IThesaurusExtractInfo, IObjectRemovedEvent)
def handleRemovedExtractInfo(extract, event):
    thesaurus = getParent(extract, IThesaurus)
    name = getName(extract)
    for term in thesaurus.terms:
        term.removeExtract(name, check=False)


class ThesaurusExtractsContainer(Folder):
    """Thesaurus extracts container"""

    implements(IThesaurusExtracts)


THESAURUS_EXTRACTS_KEY = 'ztfy.thesaurus.extracts'

@adapter(IThesaurus)
@implementer(IThesaurusExtracts)
def ThesaurusExtractsFactory(context):
    """Thesaurus extracts adapter"""
    annotations = IAnnotations(context)
    extracts = annotations.get(THESAURUS_EXTRACTS_KEY)
    if extracts is None:
        extracts = annotations[THESAURUS_EXTRACTS_KEY] = ThesaurusExtractsContainer()
        locate(extracts, context, '++extracts++')
    return extracts
