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
from zope.schema.interfaces import IObject, IList, SchemaNotProvided

# import local interfaces

# import Zope3 packages
from zope.interface import implements, Interface
from zope.schema import Object, List, Set, Choice, TextLine

# import local packages

from ztfy.thesaurus import _


class IThesaurusTermField(IObject):
    """Marker interface to define a thesaurus term field"""

    thesaurus_name = TextLine(title=_("Thesaurus name"),
                              required=False)

    extract_name = TextLine(title=_("Extract name"),
                            required=False)


class IThesaurusTermsListField(IList):
    """Marker interface to define a list of thesaurus terms"""

    thesaurus_name = TextLine(title=_("Thesaurus name"),
                              required=False)

    extract_name = TextLine(title=_("Extract name"),
                            required=False)


class ThesaurusTermField(Object):
    """Thesaurus term schema field"""

    implements(IThesaurusTermField)

    def __init__(self, schema=None, thesaurus_name=u'', extract_name=u'', **kw):
        super(ThesaurusTermField, self).__init__(schema=Interface, **kw)
        self.thesaurus_name = thesaurus_name
        self.extract_name = extract_name

    def _validate(self, value):
        super(Object, self)._validate(value)
        # schema has to be provided by value
        if not self.schema.providedBy(value):
            raise SchemaNotProvided


class ThesaurusTermsListField(List):
    """Thesaurus terms list schema field"""

    implements(IThesaurusTermsListField)

    def __init__(self, value_type=None, unique=False, thesaurus_name=u'', extract_name=u'', **kw):
        super(ThesaurusTermsListField, self).__init__(value_type=Object(schema=Interface), unique=False, **kw)
        self.thesaurus_name = thesaurus_name
        self.extract_name = extract_name


class ValidatedSet(Set):
    """A set field validated when not bound to a context"""

    def _validate(self, value):
        #Don't try to validate with empty context !
        if self.context is None:
            return
        super(ValidatedSet, self)._validate(value)


class ValidatedChoice(Choice):
    """An always validated choice field"""

    def _validate(self, value):
        pass
