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
from zope.catalog.interfaces import ICatalog
from zope.container.interfaces import IContainer

# import local interfaces
from ztfy.security.interfaces import ILocalRoleManager
from ztfy.thesaurus.interfaces.term import IThesaurusTerm

# import Zope3 packages
from zope.container.constraints import contains
from zope.interface import Interface, Attribute
from zope.location.interfaces import IContained
from zope.schema import Text, TextLine, Choice, Object, List, Date
from ztfy.security.schema import PrincipalList

# import local packages
from ztfy.utils.schema import ColorField

from ztfy.thesaurus import _


class IThesaurusInfoBase(Interface):
    """Thesaurus base info"""

    title = TextLine(title=_("thesaurus-title-title", "Title"),
                     description=_("thesaurus-title-description", "Long title for thie thesaurus"),
                     required=False)

    subject = TextLine(title=_("thesaurus-subject-title", "Subject"),
                       required=False)

    description = Text(title=_("thesaurus-description-title", "Description"),
                       required=False)

    language = Choice(title=_("thesaurus-language-title", "Language"),
                      description=_("thesaurus-language-description", "Thesaurus's language"),
                      required=False,
                      default='fr',
                      vocabulary='ZTFY base languages')

    creator = TextLine(title=_("thesaurus-creator-title", "Creator"),
                       required=False)

    publisher = TextLine(title=_("thesaurus-publisher-title", "Publisher"),
                         required=False)

    created = Date(title=_("thesaurus-created-title", "Creation date"),
                   required=False)


class IThesaurusInfo(IThesaurusInfoBase):
    """Main thesaurus infos"""

    name = TextLine(title=_("thesaurus-name-title", "Name"),
                    description=_("thesaurus-name-description", "Thesaurus's name"),
                    required=True,
                    readonly=True)

    terms = Attribute(_("thesaurus-terms-title", "Thesaurus terms"))

    catalog = Object(title=_("thesaurus-catalog-title", "Thesaurus catalog"),
                     description=_("thesaurus-catalog-description", "Inner thesaurus catalog, used for full-text indexing"),
                     schema=ICatalog)

    def findTerms(self, query=None, extract=None, autoexpand='on_miss', glob='end'):
        """Get terms matching given query and parent
        
        @param query: the text query
        @param autoexpand: can be True, False on 'on_miss' (default)
        @param glob: can be 'start' (default), 'end', 'both' or None
        """


class IThesaurusContentInfo(Interface):
    """Thesaurus content infos"""

    top_terms = List(title=_("thesaurus-topterms-title", "Thesaurus top-terms"),
                     description=_("thesaurus-topterms-description", "List of top thesaurus terms, placed at first level"),
                     required=False,
                     value_type=Object(schema=IThesaurusTerm))


class IThesaurusWriter(Interface):
    """Thesaurus update interface"""

    def initCatalog(self):
        """Initialize thesaurus catalog"""

    def delete(self):
        """Delete thesaurus"""


class IThesaurusContentWriter(Interface):
    """Thesaurus content update interface"""

    def clear(self):
        """Clear thesaurus contents"""

    def load(self, configuration):
        """Load contents from given configuration"""

    def merge(self, configuration, thesaurus=None):
        """Merge current thesaurus with another one for given configuration"""

    def resetTermsParent(self):
        """Reset thesaurus terms parent attribute"""

    def resetTopTerms(self):
        """Reset thesaurus top terms"""


class IThesaurusAdminRole(Interface):
    """Thesaurus administrators roles interface"""

    administrators = PrincipalList(title=_("Administrators"),
                                   description=_("List of thesaurus's administrators"),
                                   required=False)


class IThesaurusContribRole(Interface):
    """Thesaurus administrators roles interface"""

    contributors = PrincipalList(title=_("Contents managers"),
                                 description=_("List of thesaurus's contents contributors"),
                                 required=False)


class IThesaurusRoles(IThesaurusAdminRole, IThesaurusContribRole):
    """Thesaurus roles interface"""


class IThesaurus(IThesaurusInfo, IThesaurusContentInfo, IThesaurusWriter, IThesaurusContentWriter,
                 IThesaurusRoles, IContained, ILocalRoleManager):
    """Thesaurus interface"""


class IThesaurusManagerTarget(Interface):
    """Marker interface for contents managing thesaurus"""


class IThesaurusTarget(Interface):
    """Marker interface for contents indexed on a thesaurus base"""


class IThesaurusExtractBaseInfo(Interface):
    """Thesaurus extract base info"""

    name = TextLine(title=_("extract-title-title", "Extract name"),
                     description=_("extract-title-description", "Extract title"),
                     required=True)

    description = Text(title=_("extract-description-title", "Description"),
                       required=False)

    abbreviation = TextLine(title=_("extract-abbr-title", "Abbreviation"),
                            description=_("extract-abbr-description", "Short abbreviation used to distinguish the extract"),
                            required=True,
                            max_length=3)

    color = ColorField(title=_("Extract color"),
                       description=_("A color associated with this extract"),
                       required=True)

    managers = PrincipalList(title=_("Extract managers"),
                             description=_("List of principals which can manage extract contents"),
                             required=False)


class IThesaurusExtractWriter(Interface):
    """Thesaurus extract writer"""

    def addTerm(self, term):
        """Add a term to this extract"""

    def removeTerm(self, term):
        """Remove a term from this extract"""


class IThesaurusExtractInfo(IThesaurusExtractBaseInfo, IThesaurusExtractWriter, ILocalRoleManager):
    """Thesaurus extract info"""


class IThesaurusExtracts(IContainer):
    """Thesaurus extracts container interface"""

    contains(IThesaurusExtractInfo)
