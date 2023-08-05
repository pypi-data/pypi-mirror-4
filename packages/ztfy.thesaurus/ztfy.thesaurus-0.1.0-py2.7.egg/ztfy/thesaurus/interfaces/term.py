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
from zope.container.interfaces import IContainer

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import Text, TextLine, Bool, Choice, Int, Datetime, Set
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

# import local packages
from ztfy.thesaurus.schema import ThesaurusTermField, ThesaurusTermsListField, ValidatedSet

from ztfy.thesaurus import _


THESAURUS_STATUS = (u'candidate',
                    u'published',
                    u'archived')

THESAURUS_STATUS_LABELS = (_("Candidate"),
                           _("Published"),
                           _("Archived"))

THESAURUS_STATUS_VOCABULARY = SimpleVocabulary([SimpleTerm(THESAURUS_STATUS[i], t, t) for i, t in enumerate(THESAURUS_STATUS_LABELS)])


class IThesaurusTermInfo(Interface):
    """Thesaurus term base interface"""

    id = Attribute(_("term-id", "Internal ID"))

    label = TextLine(title=_("term-label-title", "Term label"),
                     description=_("term-label-description", "Full keyword for the given term"),
                     required=True)

    caption = Attribute(_("term-caption", "Term external caption"))

    alt = TextLine(title=_("term-alt-title", "Alternate label"),
                   required=False)

    definition = Text(title=_("term-definition-title", "Definition"),
                      description=_("term-definition-description", "Long definition, mostly for complicated terms"),
                      required=False)

    note = Text(title=_("term-note-title", "Term's application note"),
                description=_("term-note-description", "Application note for the given term"),
                required=False)

    generic = ThesaurusTermField(title=_("term-generic-title", "Generic term"),
                                 description=_("term-generic-description", "Parent generic term of the current term"),
                                 required=False)

    specifics = ThesaurusTermsListField(title=_("term-specifics-title", "Specifics terms"),
                                        description=_("term-specifics-description", "Child more specifics terms of the current term"),
                                        required=False)

    associations = ThesaurusTermsListField(title=_("term-associations-title", "Associated terms"),
                                           description=_("term-associations-description", "Other terms associated to the current term"),
                                           required=False)

    usage = ThesaurusTermField(title=_("term-usage-title", "Usage"),
                               description=_("term-usage-description", "For synonyms, specify here the term's descriptor to use"),
                               required=False)

    used_for = ThesaurusTermsListField(title=_("term-usedfor-title", "Synonyms"),
                                       description=_("term-usedfor-description", "For a given allowed descriptor, specify here the list of synonyms"),
                                       required=False)

    extracts = ValidatedSet(title=_("term-extracts-title", "Extracts"),
                            description=_("term-extracts-description", "List of thesaurus extracts including this term"),
                            required=False,
                            value_type=Choice(vocabulary='ZTFY thesaurus extracts'))

    extensions = Set(title=_("term-extensions-title", "Extensions"),
                     description=_(""),
                     required=False,
                     value_type=Choice(vocabulary='ZTFY thesaurus term extensions'))

    status = Choice(title=_("term-status-title", "Status"),
                    description=_("term-status-description", "Term status"),
                    required=True,
                    vocabulary=THESAURUS_STATUS_VOCABULARY,
                    default=u'published')

    level = Int(title=_("term-level-title", "Level"),
                description=_("term-level-description", "Term's level in the thesaurus tree"),
                required=True,
                readonly=True,
                default=1)

    micro_thesaurus = Bool(title=_("term-miro-title", "Micro-thesaurus ?"),
                           description=_("term-micro-description", "Is the term part of a micro-thesaurus"),
                           required=False)

    parent = ThesaurusTermField(title=_("term-parent-title", "First level parent"),
                                description=_("term-parent-description", "Parent at level 1 of the current term, or None"),
                                required=False,
                                schema=Interface)

    created = Datetime(title=_("term-created-title", "Creation date"),
                       required=False)

    modified = Datetime(title=_("term-modified-title", "Modification date"),
                        required=False)

    def getParents(self):
        """Get list of term's parents"""

    def getParentChilds(self):
        """Get 'brother's terms of current term"""

    def getAllChilds(self, terms=None, with_synonyms=False):
        """Get full list of term's specifics"""

    def queryExtensions(self):
        """Get list of extension utilities"""


class IThesaurusTermWriter(Interface):
    """Thesaurus term writer interface"""

    def merge(self, term):
        """Merge term attributes with given term, to avoid overwriting all entity"""


class IThesaurusTermExtractsWriter(Interface):
    """Thesaurus term extracts writer"""

    def addExtract(self, extract, check=True):
        """Add given extract to the list of term extracts"""

    def removeExtract(self, extract, check=True):
        """Remove given extract from the list of term extracts"""


class IThesaurusTerm(IThesaurusTermInfo, IThesaurusTermWriter, IThesaurusTermExtractsWriter):
    """Thesaurus term interface"""


IThesaurusTermInfo['generic'].schema = IThesaurusTerm
IThesaurusTermInfo['usage'].schema = IThesaurusTerm
IThesaurusTermInfo['parent'].schema = IThesaurusTerm


class IThesaurusTermsIterable(Interface):
    """Thesaurus terms iterator interface"""

    def iterkeys(self):
        "Iterate over keys; equivalent to __iter__"

    def itervalues(self):
        "Iterate over values"

    def iteritems(self):
        "Iterate over items"


class IThesaurusTermsContainer(IContainer, IThesaurusTermsIterable):
    """Thesaurus terms container interface"""
