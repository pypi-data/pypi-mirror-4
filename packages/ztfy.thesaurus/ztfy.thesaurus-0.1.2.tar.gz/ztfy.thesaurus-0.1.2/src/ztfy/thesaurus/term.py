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
from datetime import datetime

# import Zope3 interfaces

# import local interfaces
from ztfy.thesaurus.interfaces.extension import IThesaurusTermExtension
from ztfy.thesaurus.interfaces.thesaurus import IThesaurusExtractInfo
from ztfy.thesaurus.interfaces.term import IThesaurusTerm
from ztfy.thesaurus.interfaces.tree import INode

# import Zope3 packages
from zope.component import adapts, queryUtility
from zope.container.contained import Contained
from zope.interface import implements, noLongerProvides, alsoProvides
from zope.schema.fieldproperty import FieldProperty
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getName

# import local packages
from ztfy.utils.timezone import tztime


class ThesaurusTerm(Persistent, Contained):
    """Thesaurus term content"""

    implements(IThesaurusTerm)

    label = FieldProperty(IThesaurusTerm['label'])
    alt = FieldProperty(IThesaurusTerm['alt'])
    definition = FieldProperty(IThesaurusTerm['definition'])
    note = FieldProperty(IThesaurusTerm['note'])
    _generic = FieldProperty(IThesaurusTerm['generic'])
    _specifics = FieldProperty(IThesaurusTerm['specifics'])
    _associations = FieldProperty(IThesaurusTerm['associations'])
    _usage = FieldProperty(IThesaurusTerm['usage'])
    _used_for = FieldProperty(IThesaurusTerm['used_for'])
    _extracts = FieldProperty(IThesaurusTerm['extracts'])
    _extensions = FieldProperty(IThesaurusTerm['extensions'])
    status = FieldProperty(IThesaurusTerm['status'])
    level = FieldProperty(IThesaurusTerm['level'])
    micro_thesaurus = FieldProperty(IThesaurusTerm['micro_thesaurus'])
    _parent = FieldProperty(IThesaurusTerm['parent'])
    _created = FieldProperty(IThesaurusTerm['created'])
    _modified = FieldProperty(IThesaurusTerm['modified'])

    def __init__(self, label, alt=None, definition=None, note=None, generic=None, specifics=[], associations=[],
                 usage=None, used_for=[], created=None, modified=None):
        self.label = label
        self.alt = alt
        self.definition = definition
        self.note = note
        self.generic = generic
        self.specifics = specifics
        self.associations = associations
        self.usage = usage
        self.used_for = used_for
        self.created = created
        self.modified = modified

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return isinstance(other, ThesaurusTerm) and (self.label == other.label)

    @property
    def caption(self):
        if self._usage:
            return '%s [%s]' % (self._usage.label,
                                ', '.join((term.label for term in self._usage._used_for)))
        elif self._used_for:
            return '%s [%s]' % (self.label,
                                ', '.join((term.label for term in self._used_for)))
        else:
            return self.label

    @property
    def generic(self):
        return self._generic

    @generic.setter
    def generic(self, value):
        self._generic = generic = removeSecurityProxy(value)
        if (generic is not None) and generic.extracts:
            self.extracts = (self.extracts or set()) & generic.extracts
        else:
            self.extracts = set()

    @property
    def specifics(self):
        return self._specifics

    @specifics.setter
    def specifics(self, value):
        self._specifics = [removeSecurityProxy(term) for term in value or ()]

    @property
    def associations(self):
        return self._associations

    @associations.setter
    def associations(self, value):
        self._associations = [removeSecurityProxy(term) for term in value or ()]

    @property
    def usage(self):
        return self._usage

    @usage.setter
    def usage(self, value):
        self._usage = removeSecurityProxy(value)

    @property
    def used_for(self):
        return self._used_for

    @used_for.setter
    def used_for(self, value):
        self._used_for = [removeSecurityProxy(term) for term in value or ()]

    @property
    def extracts(self):
        return self._extracts

    @extracts.setter
    def extracts(self, value):
        old_value = self._extracts or set()
        new_value = value or set()
        if self._generic is not None:
            new_value = new_value & (self._generic.extracts or set())
        if old_value != new_value:
            removed = old_value - new_value
            if removed:
                for term in self.specifics:
                    term.extracts = (term.extracts or set()) - removed
            self._extracts = removeSecurityProxy(new_value)

    def addExtract(self, extract, check=True):
        if IThesaurusExtractInfo.providedBy(extract):
            extract = getName(extract)
        if check:
            self.extracts = (self.extracts or set()) | set((extract,))
        else:
            self._extracts = removeSecurityProxy((self._extracts or set()) | set((extract,)))

    def removeExtract(self, extract, check=True):
        if IThesaurusExtractInfo.providedBy(extract):
            extract = getName(extract)
        if check:
            self.extracts = (self.extracts or set()) - set((extract,))
        else:
            self._extracts = removeSecurityProxy((self._extracts or set()) - set((extract,)))

    @property
    def extensions(self):
        return self._extensions or set()

    @extensions.setter
    def extensions(self, value):
        old_value = self._extensions or set()
        new_value = value or set()
        if old_value != new_value:
            added = new_value - old_value
            removed = old_value - new_value
            for ext in removed:
                extension = queryUtility(IThesaurusTermExtension, ext)
                if extension is not None:
                    noLongerProvides(self, extension.target_interface)
            for ext in added:
                extension = queryUtility(IThesaurusTermExtension, ext)
                if extension is not None:
                    alsoProvides(self, extension.target_interface)
            self._extensions = removeSecurityProxy(new_value)

    def queryExtensions(self):
        return [ util for util in [ queryUtility(IThesaurusTermExtension, ext) for ext in self.extensions ]
                               if util is not None ]

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = removeSecurityProxy(value)

    @property
    def created(self):
        return self._created

    @created.setter
    def created(self, value):
        if isinstance(value, (str, unicode)):
            if ' ' in value:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            else:
                value = datetime.strptime(value, '%Y-%m-%d')
        self._created = tztime(value)

    @property
    def modified(self):
        return self._modified

    @modified.setter
    def modified(self, value):
        if isinstance(value, (str, unicode)):
            if ' ' in value:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            else:
                value = datetime.strptime(value, '%Y-%m-%d')
        self._modified = tztime(value)

    def getParents(self):
        terms = []
        parent = self.generic
        while parent is not None:
            terms.append(parent)
            parent = parent.generic
        return terms

    @property
    def level(self):
        return len(self.getParents()) + 1

    def getParentChilds(self):
        terms = []
        parent = self.generic
        if parent is not None:
            [ terms.append(term) for term in parent.specifics if term is not self ]
        return terms

    def getAllChilds(self, terms=None, with_synonyms=False):
        if terms is None:
            terms = []
        if with_synonyms:
            terms.extend(self.used_for)
        terms.extend(self.specifics)
        for term in self.specifics:
            term.getAllChilds(terms, with_synonyms)
        return terms

    def merge(self, term):
        if term is None:
            return
        # assign basic attributes
        for name in ('label', 'definition', 'note', 'status', 'micro_thesaurus', 'created', 'modified'):
            setattr(self, name, getattr(term, name, None))
        # for term references, we have to check if the target term is already
        # in our parent thesaurus or not :
        #  - if yes => we target the term actually in the thesaurus
        #  - if not => we keep the same target, which will be included in the thesaurus after merging
        for name in ('generic', 'usage'):
            target = getattr(term, name)
            if target is None:
                setattr(self, name, None)
            else:
                if target.label in self.__parent__.keys():
                    setattr(self, name, self.__parent__[target.label])
                else:
                    setattr(self, name, target)
        for name in ('specifics', 'associations', 'used_for'):
            targets = getattr(term, name, [])
            if not targets:
                setattr(self, name, [])
            else:
                new_targets = []
                for target in targets:
                    if target.label in self.__parent__.keys():
                        new_targets.append(self.__parent__[target.label])
                    else:
                        new_targets.append(target)
                setattr(self, name, new_targets)


class ThesaurusTermTreeAdapter(object):
    """Thesaurus term tree adapter"""

    adapts(IThesaurusTerm)
    implements(INode)

    def __init__(self, context):
        self.context = context

    @property
    def cssClass(self):
        return self.context.status

    @property
    def label(self):
        return self.context.label

    def getLevel(self):
        return self.context.level

    def hasChildren(self):
        return len(self.context.specifics) > 0

    def getChildren(self):
        return self.context.specifics
