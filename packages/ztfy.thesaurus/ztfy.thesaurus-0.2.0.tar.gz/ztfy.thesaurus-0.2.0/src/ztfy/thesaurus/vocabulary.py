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
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ztfy.thesaurus.interfaces.extension import IThesaurusTermExtension
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusExtracts

# import Zope3 packages
from zope.i18n import translate
from zope.interface import classProvides
from zope.component import getUtilitiesFor
from zope.componentvocabulary.vocabulary import UtilityVocabulary
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.traversing.api import getName

# import local packages
from ztfy.utils.request import queryRequest
from ztfy.utils.traversing import getParent
from zope.component.interfaces import ComponentLookupError


class ThesaurusVocabulary(UtilityVocabulary):
    """Thesaurus utilities vocabulary"""

    classProvides(IVocabularyFactory)

    interface = IThesaurus
    nameOnly = False


class ThesaurusNamesVocabulary(UtilityVocabulary):
    """Thesaurus names utilities vocabulary"""

    classProvides(IVocabularyFactory)

    interface = IThesaurus
    nameOnly = True


class ThesaurusExtractsVocabulary(SimpleVocabulary):
    """Thesaurus extracts vocabulary"""

    classProvides(IVocabularyFactory)

    def __init__(self, context=None):
        terms = []
        if context is not None:
            thesaurus = getParent(context, IThesaurus)
            if thesaurus is not None:
                extracts = IThesaurusExtracts(thesaurus)
                terms = [ SimpleTerm(getName(extract), title=extract.name) for extract in extracts.values() ]
                terms.sort(key=lambda x: x.title)
        super(ThesaurusExtractsVocabulary, self).__init__(terms)


class ThesaurusTermExtensionsVocabulary(SimpleVocabulary):
    """Thesaurus term extensions vocabulary"""

    classProvides(IVocabularyFactory)

    interface = IThesaurusTermExtension
    nameOnly = False

    def __init__(self, context, **kw):
        request = queryRequest()
        try:
            utils = getUtilitiesFor(self.interface, context)
            terms = [ SimpleTerm(name, title=translate(util.label, context=request))
                      for name, util in utils ]
        except ComponentLookupError:
            terms = []
        super(ThesaurusTermExtensionsVocabulary, self).__init__(terms)
