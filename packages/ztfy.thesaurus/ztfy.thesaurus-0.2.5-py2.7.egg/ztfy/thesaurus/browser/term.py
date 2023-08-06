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
from z3c.form.interfaces import DISPLAY_MODE, IErrorViewSnippet

# import local interfaces
from ztfy.thesaurus.interfaces.term import IThesaurusTermInfo
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus

# import Zope3 packages
from z3c.form import field
from zope.component import getMultiAdapter
from zope.interface import Invalid
from zope.security.proxy import removeSecurityProxy
from zope.traversing import api as traversing_api

# import local packages
from ztfy.skin.form import DialogAddForm, DialogEditForm
from ztfy.skin.menu import DialogMenuItem
from ztfy.thesaurus.browser.tree import ThesaurusTermsTreeView
from ztfy.thesaurus.term import ThesaurusTerm
from ztfy.utils.request import setRequestData, getRequestData
from ztfy.utils.traversing import getParent

from ztfy.thesaurus import _


class ThesaurusTermAddForm(DialogAddForm):
    """Thesaurus term add form"""

    fields = field.Fields(IThesaurusTermInfo).select('label', 'alt', 'definition', 'note',
                                                     'generic', 'associations', 'usage',
                                                     'extensions', 'status', 'created')

    legend = _("Add new term")

    parent_interface = IThesaurus
    parent_view = ThesaurusTermsTreeView

    @property
    def title(self):
        return getParent(self.context, IThesaurus).title

    def extractData(self, setErrors=True):
        data, errors = super(ThesaurusTermAddForm, self).extractData(setErrors=setErrors)
        if data.get('label') in IThesaurus(self.context).terms:
            error = Invalid(_("New label already in use"))
            widget = self.widgets['label']
            view = getMultiAdapter((error, self.request, widget, widget.field, self, self.context),
                                   IErrorViewSnippet)
            view.update()
            errors += (view,)
            if setErrors:
                widget.error = view
                self.widgets.errors = errors
        return data, errors

    def create(self, data):
        result = ThesaurusTerm(data.get('label'))
        setRequestData('thesaurus.new_term', result, self.request)
        return result

    def add(self, term):
        thesaurus = IThesaurus(self.context)
        thesaurus.terms[term.label] = term

    def updateContent(self, term, data):
        super(ThesaurusTermAddForm, self).updateContent(term, data)
        generic = term.generic
        usage = term.usage
        if (generic is None) and (usage is None):
            thesaurus = IThesaurus(self.context)
            thesaurus.top_terms = thesaurus.top_terms + [term, ]
        else:
            if generic is not None:
                generic.specifics = generic.specifics + [term, ]
            elif usage is not None:
                usage.used_for = usage.used_for + [term, ]

    def getOutput(self, writer, parent):
        term = getRequestData('thesaurus.new_term', self.request)
        if (term is None) or not term.generic:
            return writer.write({ 'output': u'RELOAD' })
        else:
            return writer.write({ 'output': u'CALLBACK',
                                  'callback': '$.ZTFY.thesaurus.tree.reloadTerm',
                                  'options': { 'source': term.generic.label.replace("'", "&#039;") } })


class ThesaurusTermAddMenuItem(DialogMenuItem):
    """Thesaurus term add menu item"""

    title = _(":: Add term...")
    target = ThesaurusTermAddForm


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
        self.widgets['used_for'].mode = DISPLAY_MODE
        self.widgets['extracts'].mode = DISPLAY_MODE
        self.widgets['created'].mode = DISPLAY_MODE

    def extractData(self, setErrors=True):
        data, errors = super(ThesaurusTermEditForm, self).extractData(setErrors=setErrors)
        label = data.get('label')
        if (label != self.context.label) and (data.get('label') in traversing_api.getParent(self.context)):
            error = Invalid(_("New label already in use"))
            widget = self.widgets['label']
            view = getMultiAdapter((error, self.request, widget, widget.field, self, self.context),
                                   IErrorViewSnippet)
            view.update()
            if setErrors:
                widget.error = view
                self.widgets.errors = errors
            errors += (view,)
        return data, errors

    def applyChanges(self, data):
        term = self.getContent()
        thesaurus = getParent(term, IThesaurus)
        old_label = term.label
        old_generic = term.generic
        old_usage = term.usage
        changes = super(ThesaurusTermEditForm, self).applyChanges(data)
        # Move term if label changed
        # Don't use IObjectMover interface to avoid cataloging problems...
        if 'label' in changes.get(IThesaurusTermInfo, []):
            parent = traversing_api.getParent(term)
            del parent[old_label]
            parent[term.label] = term
        # Check terms and thesaurus top terms if generic or usage changed
        self._v_generic_changed = old_generic != term.generic
        self._v_usage_changed = old_usage != term.usage
        if self._v_generic_changed:
            # Check previous value
            if old_generic is not None:
                # add a previous generic?
                # remove term from list of previous generic's specifics
                specifics = removeSecurityProxy(old_generic.specifics)
                if term in specifics:
                    specifics.remove(term)
                    old_generic.specifics = specifics
            else:
                # didn't have a generic?
                # may remove term from thesaurus top terms
                top_terms = removeSecurityProxy(thesaurus.top_terms)
                if term in top_terms:
                    top_terms.remove(term)
                    thesaurus.top_terms = top_terms
            # Check new value
            if term.generic is None:
                # no generic and not a synonym?
                # term should be added to thesaurus top terms
                if (term.usage is None) and (term not in thesaurus.top_terms):
                    thesaurus.top_terms = thesaurus.top_terms + [term, ]
            else:
                # new generic ?
                # add term to generic's specific terms
                if term not in term.generic.specifics:
                    term.generic.specifics = term.generic.specifics + [term, ]
        if self._v_usage_changed:
            # Check previous value
            if old_usage is not None:
                # add a previous usage term?
                used_for = removeSecurityProxy(old_usage.used_for)
                if term in used_for:
                    used_for.remove(term)
                    old_usage.used_for = used_for
            # Check new term usage
            if term.usage is None:
                # no usage? Maybe a top term...
                if (term.generic is None) and (term not in thesaurus.top_terms):
                    thesaurus.top_terms = thesaurus.top_terms + [term, ]
            else:
                # term usage?
                # remove term from top-terms...
                top_terms = removeSecurityProxy(thesaurus.top_terms)
                if term in top_terms:
                    top_terms.remove(term)
                    thesaurus.top_terms = top_terms
                # add term to usage's synonyms
                if term not in term.usage.used_for:
                    term.usage.used_for = term.usage.used_for + [term, ]
        return changes

    def getOutput(self, writer, parent, changes=()):
        callback = None
        options = None
        if self._v_generic_changed:
            status = u'RELOAD'
        else:
            term_changes = changes.get(IThesaurusTermInfo, [])
            if ('label' in term_changes) or ('status' in term_changes):
                term = self.getContent()
                generic = term.generic
                if generic is None:
                    status = u'RELOAD'
                else:
                    status = u'CALLBACK'
                    callback = '$.ZTFY.thesaurus.tree.reloadTerm'
                    options = { 'source': generic.label.replace("'", "&#039;"),
                                'status': term.status }
            else:
                status = changes and u'OK' or u'NONE'
        return writer.write({ 'output': status,
                              'callback': callback,
                              'options': options })
