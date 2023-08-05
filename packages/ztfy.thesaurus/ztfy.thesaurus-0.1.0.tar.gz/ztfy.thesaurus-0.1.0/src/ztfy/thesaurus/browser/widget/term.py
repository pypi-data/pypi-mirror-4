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
import re

# import Zope3 interfaces
from z3c.form.interfaces import IFieldWidget, IWidget
from zope.schema.interfaces import IField

# import local interfaces
from ztfy.skin.layer import IZTFYBrowserLayer
from ztfy.thesaurus.browser.widget.interfaces import IThesaurusTermFieldWidget, \
                                                     IThesaurusTermsListFieldWidget
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus
from ztfy.thesaurus.schema import IThesaurusTermField, IThesaurusTermsListField

# import Zope3 packages
from z3c.form.browser.text import TextWidget
from z3c.form.converter import BaseDataConverter, SequenceDataConverter
from z3c.form.widget import FieldWidget
from zope.component import adapter, adapts, getUtility, queryUtility
from zope.interface import implementer, implementsOnly
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.jqueryui import jquery_multiselect
from ztfy.thesaurus.browser import ztfy_thesaurus
from ztfy.utils.traversing import getParent
from ztfy.thesaurus.interfaces.term import IThesaurusTerm


SYNONYM = re.compile('(.*)\ \[.*\]')

class ThesaurusTermFieldDataConverter(BaseDataConverter):
    """Thesaurus term data converter"""

    adapts(IThesaurusTermField, IWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return u''
        if IThesaurusTerm.providedBy(self.widget.context):
            return unicode(value.label)
        else:
            return unicode(value.caption)

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value
        match = SYNONYM.match(value)
        if match:
            value = match.groups()[0]
        thesaurus_name = self.widget.thesaurus_name or self.field.thesaurus_name
        if thesaurus_name:
            thesaurus = getUtility(IThesaurus, thesaurus_name)
        else:
            thesaurus = getParent(self.widget.context, IThesaurus)
            if thesaurus is None:
                thesaurus = queryUtility(IThesaurus)
        if thesaurus is not None:
            return thesaurus.terms.get(value)
        else:
            return None


class ThesaurusTermWidget(TextWidget):
    """Thesaurus term widget"""

    implementsOnly(IThesaurusTermFieldWidget)

    thesaurus_name = FieldProperty(IThesaurusTermFieldWidget['thesaurus_name'])
    extract_name = FieldProperty(IThesaurusTermFieldWidget['extract_name'])

    def update(self):
        super(ThesaurusTermWidget, self).update()
        self.thesaurus_name = self.field.thesaurus_name or u''
        self.extract_name = self.field.extract_name or u''

    def render(self):
        jquery_multiselect.need()
        ztfy_thesaurus.need()
        return super(ThesaurusTermWidget, self).render()


@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def ThesaurusTermFieldWidget(field, request):
    return FieldWidget(field, ThesaurusTermWidget(request))



class ThesaurusTermsListFieldDataConverter(SequenceDataConverter):
    """Thesaurus terms list data converter"""

    adapts(IThesaurusTermsListField, IWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return []
        if IThesaurusTerm.providedBy(self.widget.context):
            return '|'.join([term.label for term in value])
        else:
            return '|'.join([term.caption for term in value])

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value
        value = value.split('|')
        for idx, val in enumerate(value[:]):
            match = SYNONYM.match(val)
            if match:
                value[idx] = match.groups()[0]
        thesaurus_name = self.widget.thesaurus_name or self.field.thesaurus_name
        if thesaurus_name:
            thesaurus = getUtility(IThesaurus, thesaurus_name)
        else:
            thesaurus = getParent(self.widget.context, IThesaurus)
            if thesaurus is None:
                thesaurus = queryUtility(IThesaurus)
        if thesaurus is not None:
            terms = thesaurus.terms
            return [terms[term] for term in value]
        else:
            return []


class ThesaurusTermsListWidget(TextWidget):
    """Thesaurus terms list widget"""

    implementsOnly(IThesaurusTermsListFieldWidget)

    thesaurus_name = FieldProperty(IThesaurusTermFieldWidget['thesaurus_name'])
    extract_name = FieldProperty(IThesaurusTermFieldWidget['extract_name'])

    size = 10
    multiple = True

    def update(self):
        super(ThesaurusTermsListWidget, self).update()
        self.thesaurus_name = self.field.thesaurus_name or u''
        self.extract_name = self.field.extract_name or u''

    def updateTerms(self):
        self.terms = []
        return self.terms

    def render(self):
        jquery_multiselect.need()
        ztfy_thesaurus.need()
        return super(ThesaurusTermsListWidget, self).render()


@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def ThesaurusTermsListFieldWidget(field, request):
    return FieldWidget(field, ThesaurusTermsListWidget(request))
