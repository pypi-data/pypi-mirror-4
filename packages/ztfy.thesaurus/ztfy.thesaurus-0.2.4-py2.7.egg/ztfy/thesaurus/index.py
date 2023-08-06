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
from ztfy.thesaurus.interfaces.index import IThesaurusTermFieldIndex, IThesaurusTermsListFieldIndex

# import Zope3 packages
from zc.catalog.catalogindex import ValueIndex, SetIndex
from zc.catalog.index import SetIndex as SetIndexBase, ValueIndex as ValueIndexBase
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages


class ThesaurusTermFieldIndex(ValueIndex):
    """Thesaurus term field index"""

    implements(IThesaurusTermFieldIndex)

    thesaurus_name = FieldProperty(IThesaurusTermFieldIndex['thesaurus_name'])

    def index_doc(self, docid, object):
        if self.interface is not None:
            object = self.interface(object, None)
            if object is None:
                return None
        value = getattr(object, self.field_name, None)
        if value is not None and self.field_callable:
            value = value()

        if not value:
            self.unindex_doc(docid)
            return None

        value = '%s%s' % (self.thesaurus_name + '::' if self.thesaurus_name else '', value.label)
        return ValueIndexBase.index_doc(self, docid, value)


class ThesaurusTermsListFieldIndex(SetIndex):
    """Thesaurus terms list field index"""

    implements(IThesaurusTermsListFieldIndex)

    thesaurus_name = FieldProperty(IThesaurusTermsListFieldIndex['thesaurus_name'])

    def index_doc(self, docid, object):
        if self.interface is not None:
            object = self.interface(object, None)
            if object is None:
                return None
        value = getattr(object, self.field_name, None)
        if value is not None and self.field_callable:
            value = value()

        if not value:
            self.unindex_doc(docid)
            return None

        value = [ '%s%s' % (self.thesaurus_name + '::' if self.thesaurus_name else '', term.label) for term in value ]
        return SetIndexBase.index_doc(self, docid, value)
