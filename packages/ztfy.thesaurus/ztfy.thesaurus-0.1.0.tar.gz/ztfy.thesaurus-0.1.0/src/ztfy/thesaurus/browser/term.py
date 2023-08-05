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
from z3c.form.interfaces import DISPLAY_MODE
from zope.copypastemove.interfaces import IObjectMover

# import local interfaces
from ztfy.thesaurus.interfaces.term import IThesaurusTermInfo
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus

# import Zope3 packages
from z3c.form import field
from zope.security.proxy import removeSecurityProxy
from zope.traversing import api as traversing_api

# import local packages
from ztfy.skin.form import DialogAddForm, DialogEditForm
from ztfy.skin.menu import JsMenuItem
from ztfy.thesaurus.browser.tree import ThesaurusTermsTreeView
from ztfy.thesaurus.term import ThesaurusTerm
from ztfy.utils.traversing import getParent

from ztfy.thesaurus import _


class ThesaurusTermAddMenuItem(JsMenuItem):
    """Thesaurus term add menu item"""

    title = _(":: Add term...")


class ThesaurusTermAddForm(DialogAddForm):
    """Thesaurus term add form"""

    fields = field.Fields(IThesaurusTermInfo).select('label', 'alt', 'definition', 'note',
                                                     'generic', 'associations', 'usage', 'used_for',
                                                     'extensions', 'status', 'created', 'modified')

    legend = _("Add new term")

    parent_interface = IThesaurus
    parent_view = ThesaurusTermsTreeView

    @property
    def title(self):
        return getParent(self.context, IThesaurus).title

    def create(self, data):
        thesaurus = IThesaurus(self.context)
        if data.get('label') in thesaurus.terms:
            raise ValueError, _("The given label is already used in this thesaurus !")
        return ThesaurusTerm(data.get('label'))

    def add(self, term):
        thesaurus = IThesaurus(self.context)
        thesaurus.terms[term.label] = term

    def updateContent(self, term, data):
        super(ThesaurusTermAddForm, self).updateContent(term, data)
        generic = term.generic
        if generic is None:
            thesaurus = IThesaurus(self.context)
            thesaurus.top_terms = thesaurus.top_terms + [term, ]
        else:
            generic.specifics = generic.specifics + [term, ]

    def getOutput(self, writer, parent):
        return writer.write({ 'output': u'RELOAD' })


class ThesaurusTermEditForm(DialogEditForm):
    """Thesaurus term edit form"""

    fields = field.Fields(IThesaurusTermInfo).select('label', 'alt', 'definition', 'note',
                                                     'generic', 'specifics', 'associations', 'usage', 'used_for',
                                                     'extracts', 'extensions', 'status', 'level',
                                                     'created', 'modified')

    legend = _("Edit term properties")

    parent_interface = IThesaurus
    parent_view = ThesaurusTermsTreeView

    @property
    def title(self):
        return getParent(self.context, IThesaurus).title

    def updateWidgets(self):
        super(ThesaurusTermEditForm, self).updateWidgets()
        self.widgets['specifics'].mode = DISPLAY_MODE
        self.widgets['extracts'].mode = DISPLAY_MODE

    def applyChanges(self, data):
        term = self.getContent()
        thesaurus = getParent(term, IThesaurus)
        old_generic = term.generic
        changes = super(ThesaurusTermEditForm, self).applyChanges(data)
        # Move term if label changed
        if 'label' in changes.get(IThesaurusTermInfo, []):
            IObjectMover(self.context).moveTo(traversing_api.getParent(term), term.label)
        # Check terms and thesaurus top terms if generic changed
        self._v_generic_changed = old_generic != term.generic
        if self._v_generic_changed:
            # Check previous value
            if old_generic is not None:
                # add a previous generic ?
                # remove term from list of previous generic's specifics
                specifics = removeSecurityProxy(old_generic.specifics)
                if term in specifics:
                    specifics.remove(term)
                    old_generic.specifics = specifics
            else:
                # didn't have a generic ?
                # may remove term from thesaurus top terms
                if term in thesaurus.top_terms:
                    top_terms = removeSecurityProxy(thesaurus.top_terms)
                    top_terms.remove(term)
                    thesaurus.top_terms = top_terms
            # Check new value
            if term.generic is None:
                # no generic ?
                # term should be added to thesaurus top terms
                if term not in thesaurus.top_terms:
                    thesaurus.top_terms = thesaurus.top_terms + [term, ]
            else:
                # new generic ?
                # add term to generic's specific terms
                if term not in term.generic.specifics:
                    term.generic.specifics = term.generic.specifics + [term, ]
        return changes

    def getOutput(self, writer, parent, changes=()):
        if self._v_generic_changed:
            status = u'RELOAD'
            callback = None
        else:
            if 'label' in changes.get(IThesaurusTermInfo, []):
                term = self.getContent()
                generic = term.generic
                if generic is None:
                    status = u'RELOAD'
                    callback = None
                else:
                    status = u'CALLBACK'
                    callback = """$.ZTFY.thesaurus.tree.reloadTerm("%s");""" % generic.label.replace("'", "&#039;")
            else:
                status = changes and u'OK' or u'NONE'
                callback = None
        return writer.write({ 'output': status, 'callback': callback })
