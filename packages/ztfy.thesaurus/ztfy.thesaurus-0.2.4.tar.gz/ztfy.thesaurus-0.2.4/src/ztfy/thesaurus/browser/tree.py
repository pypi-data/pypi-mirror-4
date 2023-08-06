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
from HTMLParser import HTMLParser

# import Zope3 interfaces
from z3c.json.interfaces import IJSONWriter
from zope.publisher.interfaces import NotFound

# import local interfaces
from ztfy.thesaurus.browser.interfaces.term import IThesaurusTermAddFormMenuTarget
from ztfy.thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusExtracts
from ztfy.thesaurus.interfaces.tree import ITree, INode

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import ajax, jsaction
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.traversing.api import getName
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.i18n.property import translated
from ztfy.jqueryui import jquery_datetime, jquery_multiselect
from ztfy.skin.form import DialogDisplayForm, DialogEditForm
from ztfy.skin.menu import MenuItem
from ztfy.skin.page import BaseBackView, BaseTemplateBasedPage, TemplateBasedPage
from ztfy.thesaurus.browser import ztfy_thesaurus
from ztfy.utils.property import cached_property
from ztfy.utils.traversing import getParent

from ztfy.thesaurus import _


class ThesaurusTermsTreeViewMenuItem(MenuItem):
    """Thesaurus tree view menu item"""

    title = _("Terms")


class ThesaurusTermsTreeView(BaseBackView, TemplateBasedPage, ajax.AJAXRequestHandler):
    """Thesaurus tree view"""

    implements(IThesaurusTermAddFormMenuTarget)

    legend = _("Thesaurus terms")

    _parser = HTMLParser()

    @property
    def title(self):
        return self.context.title

    def update(self):
        BaseBackView.update(self)

    def render(self):
        jquery_datetime.need()
        jquery_multiselect.need()
        ztfy_thesaurus.need()
        return super(ThesaurusTermsTreeView, self).render()

    output = render

    @cached_property
    def extracts(self):
        return IThesaurusExtracts(self.context)

    @property
    def tree(self):
        return sorted([INode(node) for node in ITree(self.context).getRootNodes()],
                      key=lambda x: x.label)

    @ajax.handler
    def getNodes(self):
        label = self.request.form.get('term')
        if label:
            label = self._parser.unescape(label)
        term = self.context.terms.get(label)
        if term is None:
            raise NotFound(self.context, label, self.request)
        extracts_container = IThesaurusExtracts(getParent(term, IThesaurus))
        result = []
        for child in INode(term).getChildren():
            node = INode(child)
            result.append({ 'label': node.label.replace("'", "&#039;"),
                            'cssClass': node.cssClass,
                            'extracts': [ { 'name': name,
                                            'title': extract.name,
                                            'color': extract.color,
                                            'used': name in (node.context.extracts or ()) } for name, extract in extracts_container.items() ],
                            'extensions': [ { 'title': translate(ext.label, context=self.request),
                                              'icon': ext.icon,
                                              'view': "%s/%s" % (absoluteURL(node.context, self.request),
                                                                 ext.target_view) } for ext in node.context.queryExtensions() ],
                            'expand': node.hasChildren() })
        writer = getUtility(IJSONWriter)
        return writer.write({ 'term': term.label,
                              'nodes': sorted(result, key=lambda x: x['label']) })

    @ajax.handler
    def switchExtract(self):
        label = self.request.form.get('term')
        if label:
            label = self._parser.unescape(label)
        term = self.context.terms.get(label)
        if term is None:
            raise NotFound(self.context, label, self.request)
        name = self.request.form.get('extract')
        if name is None:
            raise NotFound(self.context, name, self.request)
        extract = self.extracts.get(name)
        if extract is None:
            raise NotFound(self.context, name, self.request)
        writer = getUtility(IJSONWriter)
        if name in (term.extracts or set()):
            extract.removeTerm(term)
            return writer.write({ 'term': term.label,
                                  'extract': name,
                                  'used': False,
                                  'color': 'white' })
        else:
            extract.addTerm(term)
            return writer.write({ 'term': term.label,
                                  'extract': name,
                                  'used': True,
                                  'color': extract.color })


class ThesaurusExtractTermsTreeView(DialogDisplayForm):
    """Thesaurus extract terms tree view"""

    _parser = HTMLParser()

    @property
    def title(self):
        return self.thesaurus.title

    @property
    def legend(self):
        return translate(_("Terms for selected extract: %s"), context=self.request) % self.context.name

    def update(self):
        BaseBackView.update(self)
        self.updateActions()

    def render(self):
        jquery_datetime.need()
        jquery_multiselect.need()
        ztfy_thesaurus.need()
        return super(ThesaurusExtractTermsTreeView, self).render()

    output = render

    @cached_property
    def thesaurus(self):
        return getParent(self.context, IThesaurus)

    @property
    def tree(self):
        extract = getName(self.context)
        return sorted([INode(node) for node in ITree(self.thesaurus).getRootNodes()
                                            if extract in (node.extracts or ()) ],
                      key=lambda x: x.label)

    @ajax.handler
    def getNodes(self):
        label = self.request.form.get('term')
        if label:
            label = self._parser.unescape(label)
        extract_only = getName(self.context)
        term = self.thesaurus.terms.get(label)
        if term is None:
            raise NotFound(self.context, label, self.request)
        result = []
        for child in INode(term).getChildren():
            node = INode(child)
            if extract_only in (node.context.extracts or ()):
                result.append({ 'label': node.label.replace("'", "&#039;"),
                                'cssClass': node.cssClass,
                                'extracts': [],
                                'expand': node.hasChildren() })
        writer = getUtility(IJSONWriter)
        return writer.write({ 'term': term.label,
                              'nodes': sorted(result, key=lambda x: x['label']) })


#
# Thesaurus terms selector
#

class ISelectorDialogFormButtons(Interface):
    """Terms selector dialog form buttons"""

    select = jsaction.JSButton(title=_("Select terms"))
    cancel = jsaction.JSButton(title=_("Cancel"))


class ThesaurusTermsSelectorView(DialogEditForm):
    """Thesaurus terms selector tree view"""

    fields = field.Fields(Interface)
    buttons = button.Buttons(ISelectorDialogFormButtons)

    @property
    def title(self):
        return self.context.title

    @translated
    def legend(self):
        return _("Thesaurus terms selection")

    @cached_property
    def thesaurus(self):
        return getParent(self.context, IThesaurus)

    @property
    def top_terms(self):
        extract = self.request.form.get('extract')
        return sorted([term for term in self.context.top_terms
                                     if (not extract) or (extract in term.extracts) ],
                      key=lambda x: x.label)

    @jsaction.handler(buttons['select'])
    def add_handler(self, event, selector):
        return '$.ZTFY.thesaurus.tree.openSelectorAction(this.form);'

    @jsaction.handler(buttons['cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'


class ThesaurusTermsSelectorNodeView(BaseTemplateBasedPage):
    """Thesaurus terms selector node view"""

    @property
    def sub_terms(self):
        extract = self.request.form.get('extract')
        return sorted([term for term in self.context.specifics
                                     if (not extract) or (extract in term.extracts) ],
                      key=lambda x: x.label)
