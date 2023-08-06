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
import logging
logger = logging.getLogger('ztfy.thesaurus')

# import Zope3 interfaces
from z3c.form.interfaces import DISPLAY_MODE
from z3c.json.interfaces import IJSONWriter
from zope.copypastemove.interfaces import IObjectMover
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import IVocabularyFactory
from zope.size.interfaces import ISized

# import local interfaces
from ztfy.blog.browser.interfaces.container import ITitleColumn, IActionsColumn, \
                                                   IContainerTableViewTitleCell, IContainerTableViewActionsCell
from ztfy.security.interfaces import ISecurityManager
from ztfy.skin.interfaces import IContainedDefaultView, IContainerBaseView, IDefaultView
from ztfy.skin.layer import IZTFYBrowserLayer, IZTFYBackLayer
from ztfy.thesaurus.browser.interfaces.thesaurus import IThesaurusAddFormMenuTarget, \
                                                        IThesaurusExtractAddFormMenuTarget
from ztfy.thesaurus.interfaces.loader import IThesaurusLoader, IThesaurusLoaderConfiguration, \
                                             IThesaurusUpdaterConfiguration, \
                                             IThesaurusExporter, IThesaurusExporterConfiguration
from ztfy.thesaurus.interfaces.thesaurus import IThesaurusInfoBase, IThesaurusInfo, \
                                                IThesaurus, IThesaurusManagerTarget, \
                                                IThesaurusRoles, \
                                                IThesaurusExtracts, IThesaurusExtractBaseInfo, IThesaurusExtractInfo


# import Zope3 packages
from z3c.form import field, button
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget
from z3c.formjs import ajax, jsaction
from z3c.table.column import Column
from z3c.template.template import getLayoutTemplate
from zope.component import adapts, getUtility, getSiteManager, queryUtility, queryMultiAdapter
from zope.dublincore.interfaces import IZopeDublinCore
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.intid.interfaces import IIntIds
from zope.location import locate
from zope.schema import Bool
from zope.security.proxy import removeSecurityProxy
from zope.traversing import api as traversing_api
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.jqueryui import jquery_multiselect, jquery_colorpicker
from ztfy.security.browser import ztfy_security
from ztfy.security.browser.roles import RolesEditForm
from ztfy.skin.container import ContainerBaseView
from ztfy.skin.form import DialogAddForm, EditForm, DialogEditForm
from ztfy.skin.menu import MenuItem, JsMenuItem
from ztfy.thesaurus.browser import ztfy_thesaurus
from ztfy.thesaurus.loader.config import ThesaurusLoaderConfiguration, \
                                         ThesaurusUpdaterConfiguration, \
                                         ThesaurusExporterConfiguration
from ztfy.thesaurus.thesaurus import ThesaurusExtract
from ztfy.utils.container import getContentName
from ztfy.utils.list import unique
from ztfy.utils.traversing import getParent

from ztfy.thesaurus import _


class ThesaurusBackViewAdapter(object):
    """Default back-office URL adapter"""

    adapts(IThesaurus, IZTFYBackLayer, Interface)
    implements(IDefaultView)

    viewname = '@@properties.html'

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)


class ThesaurusListViewMenu(MenuItem):
    """Thesaurus list view menu"""

    title = _("Thesaurus")


class ThesaurusSizeAdapter(object):

    adapts(IThesaurus)
    implements(ISized)

    def __init__(self, context):
        self.context = context

    def sizeForSorting(self):
        return ('terms', len(self.context.terms))

    def sizeForDisplay(self):
        return _("${size} terms", mapping={'size': len(self.context.terms)})


class ThesaurusListViewTitleCellAdapter(object):

    adapts(IThesaurus, IBrowserRequest, Interface)
    implements(IContainedDefaultView)

    viewname = ''

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return '%s/@@properties.html' % absoluteURL(self.context, self.request)


class ThesaurusListView(ajax.AJAXRequestHandler, ContainerBaseView):
    """Actual list of available thesauri"""

    implements(IThesaurusAddFormMenuTarget)

    legend = _("List of registered thesauri")
    output = ContainerBaseView.render

    def update(self):
        ContainerBaseView.update(self)
        ztfy_thesaurus.need()

    @property
    def values(self):
        factory = queryUtility(IVocabularyFactory, 'ZTFY thesaurus')
        if factory is not None:
            vocabulary = factory(self.context)
            return unique([term.value for term in vocabulary])

    @ajax.handler
    def ajaxRemove(self):
        oid = self.request.form.get('oid')
        if oid is not None:
            oid = int(oid)
            intids = getUtility(IIntIds)
            thesaurus = intids.queryObject(oid)
            if IThesaurus.providedBy(thesaurus):
                thesaurus.delete()


class ThesaurusListViewActionsCellAdapter(object):

    adapts(IThesaurus, IBrowserRequest, ThesaurusListView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column

    @property
    def content(self):
        if not ISecurityManager(self.context).canUsePermission('ztfy.ManageThesaurus'):
            return ''
        klass = "ui-workflow ui-icon ui-icon-trash"
        intids = getUtility(IIntIds)
        return '''<span class="%s" title="%s" onclick="$.ZTFY.thesaurus.remove(%s,this);"></span>''' % (klass,
                                                                                                        translate(_("Delete thesaurus"), context=self.request),
                                                                                                        intids.register(self.context))


class ThesaurusAutomaticSelectWidget(SelectWidget):

    noValueMessage = _("-- automatic selection -- (if provided by selected format)")


def ThesaurusAutomaticSelectWidgetFactory(field, request):
    return FieldWidget(field, ThesaurusAutomaticSelectWidget(request))


class ThesaurusAddMenuItem(JsMenuItem):
    """Thesaurus add menu item"""

    title = _(":: Add thesaurus")


class ThesaurusAddForm(DialogAddForm):
    """Thesaurus add form"""

    title = _("Add new thesaurus")
    legend = _("Adding and registering a new thesaurus")

    layout = getLayoutTemplate()
    parent_interface = IThesaurusManagerTarget
    parent_view = ThesaurusListView

    fields = field.Fields(IThesaurusLoaderConfiguration)
    fields['language'].widgetFactory = ThesaurusAutomaticSelectWidgetFactory
    fields['encoding'].widgetFactory = ThesaurusAutomaticSelectWidgetFactory

    def create(self, data):
        configuration = ThesaurusLoaderConfiguration(data)
        loader = getUtility(IThesaurusLoader, configuration.format)
        thesaurus = loader.load(self.request.form.get(self.prefix + 'widgets.data'), configuration)
        thesaurus.name = data.get('name')
        if thesaurus.title:
            IZopeDublinCore(thesaurus).title = thesaurus.title
        else:
            IZopeDublinCore(thesaurus).title = thesaurus.name
        return thesaurus

    def updateContent(self, object, data):
        pass

    def add(self, thesaurus):
        manager = getSiteManager(self.context)
        default = manager['default']
        default['Thesaurus::' + thesaurus.name] = thesaurus
        manager.registerUtility(removeSecurityProxy(thesaurus), IThesaurus, thesaurus.name)
        locate(thesaurus, removeSecurityProxy(self.context), '++thesaurus++' + thesaurus.name)


class ThesaurusEditForm(EditForm):
    """Thesaurus edit form"""

    legend = _("Edit thesaurus properties")

    fields = field.Fields(IThesaurusInfo).select('name', 'title', 'subject', 'description', 'language',
                                                 'creator', 'publisher', 'created')

    @property
    def title(self):
        return self.context.title

    def applyChanges(self, data):
        thesaurus = self.getContent()
        old_name = thesaurus.name
        changes = super(ThesaurusEditForm, self).applyChanges(data)
        if 'name' in changes.get(IThesaurusInfo, []):
            old_parent = traversing_api.getParent(thesaurus)
            IObjectMover(thesaurus).moveTo(traversing_api.getParent(thesaurus), 'Thesaurus::' + thesaurus.name)
            manager = getSiteManager(thesaurus)
            manager.unregisterUtility(removeSecurityProxy(thesaurus), IThesaurus, old_name)
            manager.registerUtility(removeSecurityProxy(thesaurus), IThesaurus, thesaurus.name)
            locate(thesaurus, old_parent, '++thesaurus++' + thesaurus.name)
        if 'title'  in changes.get(IThesaurusInfoBase, []):
            if thesaurus.title:
                IZopeDublinCore(thesaurus).title = thesaurus.title
            else:
                IZopeDublinCore(thesaurus).title = thesaurus.name
        return changes


#
# Thesaurus roles menus and forms
#

class ThesaurusRolesMenuItem(JsMenuItem):
    """Thesaurus roles menu item"""

    title = _(":: Roles...")

    def render(self):
        ztfy_security.need()
        jquery_multiselect.need()
        return super(ThesaurusRolesMenuItem, self).render()


class ThesaurusRolesEditForm(DialogEditForm, RolesEditForm):
    """Thesaurus roles edit form"""

    interfaces = (IThesaurusRoles,)
    layout = getLayoutTemplate()
    parent_interface = IThesaurus


#
# Thesaurus extracts menus and forms
#

class ThesaurusExtractsMenuItem(MenuItem):
    """Thesaurus extract menu item"""

    title = _("Extracts")


class ThesaurusExtractNameColumn(Column):

    implements(ITitleColumn)

    header = _("Name")
    weight = 10
    cssClasses = {}

    def renderCell(self, item):
        adapter = queryMultiAdapter((item, self.request, self.table, self), IContainerTableViewTitleCell)
        prefix = (adapter is not None) and adapter.prefix or ''
        before = (adapter is not None) and adapter.before or ''
        after = (adapter is not None) and adapter.after or ''
        suffix = (adapter is not None) and adapter.suffix or ''
        title = item.name
        result = "%s%s%s" % (before, title, after)
        adapter = queryMultiAdapter((item, self.request, self.table), IContainedDefaultView)
        if adapter is None:
            adapter = queryMultiAdapter((item, self.request, self.table), IDefaultView)
        if adapter is not None:
            url = adapter.getAbsoluteURL()
            if url:
                result = '<a href="%s">%s</a>' % (url, result)
        return '%s%s%s' % (prefix, result, suffix)


class ThesaurusExtractsListViewTitleCellAdapter(object):

    adapts(IThesaurusExtractInfo, IBrowserRequest, Interface)
    implements(IContainedDefaultView)

    viewname = ''

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def getAbsoluteURL(self):
        return "javascript:$.ZTFY.dialog.open('%s/@@properties.html');" % absoluteURL(self.context, self.request)


class ThesaurusExtractsListViewCellActions(object):

    adapts(IThesaurusExtractInfo, IZTFYBrowserLayer, IContainerBaseView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column

    @property
    def content(self):
        klass = "ui-workflow ui-icon ui-icon-trash"
        intids = getUtility(IIntIds)
        thesaurus = getParent(self.context, IThesaurus)
        addr = absoluteURL(IThesaurusExtracts(thesaurus), self.request)
        return '''<span class="%s" title="%s" onclick="$.ZTFY.container.remove(%s,this, '%s/');"></span>''' % (klass,
                                                                                                               translate(_("Delete extract"), context=self.request),
                                                                                                               intids.register(self.context),
                                                                                                               addr)


class ThesaurusExtractsListView(ContainerBaseView):
    """Thesaurus extracts list view"""

    implements(IThesaurusExtractAddFormMenuTarget)

    legend = _("List of thesaurus extracts")
    output = ContainerBaseView.render

    cssClasses = { 'table': 'extracts' }

    def render(self):
        jquery_colorpicker.need()
        jquery_multiselect.need()
        ztfy_security.need()
        ztfy_thesaurus.need()
        return super(ThesaurusExtractsListView, self).render()

    @property
    def values(self):
        return IThesaurusExtracts(self.context).values()


class ThesaurusExtractAddFormMenuItem(JsMenuItem):
    """Thesaurus extract add form menu item"""

    title = _(":: Add extract...")


class IThesaurusExtractAddInfo(Interface):
    """Extra info for thesaurus extract add form"""

    add_all_terms = Bool(title=_("Add all terms in extract ?"),
                         description=_("If 'Yes', all current thesaurus terms will be affected to this extract"),
                         required=True,
                         default=True)


class ThesaurusExtractAddForm(DialogAddForm):
    """Thesaurus extract add form"""

    legend = _("Creating new thesaurus extract")

    parent_interface = IThesaurus
    parent_view = ThesaurusExtractsListView

    fields = field.Fields(IThesaurusExtractBaseInfo) + \
             field.Fields(IThesaurusExtractAddInfo)

    @property
    def title(self):
        return self.context.title

    def create(self, data):
        extract = ThesaurusExtract()
        extract.name = data.get('name')
        return extract

    def add(self, extract):
        extracts = IThesaurusExtracts(self.context)
        name = getContentName(extracts, extract.name)
        extracts[name] = extract

    def updateContent(self, extract, data):
        add_all_terms = data.pop('add_all_terms', False)
        result = super(ThesaurusExtractAddForm, self).updateContent(extract, data)
        if add_all_terms:
            thesaurus = IThesaurus(self.context)
            for term in thesaurus.terms.itervalues():
                try:
                    term.addExtract(extract, check=False)
                except:
                    logger.warning('''Resetting extracts on term "%s"''' % term.label)
                    extracts = set([ traversing_api.getName(extract) for extract in IThesaurusExtracts(thesaurus).values() ])
                    term.extracts = ((term.extracts or set()) & extracts) | set((traversing_api.getName(extract),))
        return result


class ThesaurusExtractEditForm(DialogEditForm):
    """Thesaurus extract edit form"""

    legend = _("Edit thesaurus extract properties")

    fields = field.Fields(IThesaurusExtractBaseInfo)

    @property
    def title(self):
        return translate(_('''%s: extract "%s"'''), context=self.request) % (getParent(self.context, IThesaurus).title,
                                                                             self.context.name)

    def updateWidgets(self):
        super(ThesaurusExtractEditForm, self).updateWidgets()
        self.widgets['name'].mode = DISPLAY_MODE


#
# Thesaurus merge menus and forms
#

class ThesaurusMergeMenuItem(JsMenuItem):
    """Thesaurus content edit menu item"""

    title = _(":: Merge thesaurus...")


class IMergeDialogFormButtons(Interface):
    """Export dialog form buttons"""

    add = jsaction.JSButton(title=_("Merge"))
    cancel = jsaction.JSButton(title=_("Cancel"))


class ThesaurusMergeEditForm(DialogAddForm):
    """Thesaurus merge editor"""

    legend = _("Merge thesaurus terms")

    layout = getLayoutTemplate()
    parent_interface = IThesaurus

    fields = field.Fields(IThesaurusUpdaterConfiguration).select('clear') + \
             field.Fields(IThesaurusUpdaterConfiguration).omit('name', 'clear')
    fields['language'].widgetFactory = ThesaurusAutomaticSelectWidgetFactory
    fields['encoding'].widgetFactory = ThesaurusAutomaticSelectWidgetFactory

    buttons = button.Buttons(IMergeDialogFormButtons)

    @property
    def title(self):
        return self.context.title

    @jsaction.handler(buttons['add'])
    def add_handler(self, event, selector):
        return '$.ZTFY.form.add(this.form);'

    @jsaction.handler(buttons['cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'

    def create(self, data):
        configuration = ThesaurusUpdaterConfiguration(data)
        loader = getUtility(IThesaurusLoader, configuration.format)
        thesaurus = loader.load(self.request.form.get(self.prefix + 'widgets.data'), configuration)
        target = IThesaurus(self.getContent())
        if configuration.clear:
            target.clear()
        target.merge(configuration, thesaurus)

    def updateContent(self, object, data):
        pass

    def add(self, thesaurus):
        pass


#
# Thesaurus exports menus and forms
#

class ThesaurusExportMenuItem(JsMenuItem):
    """Thesaurus export menu item"""

    title = _(":: Export thesaurus...")


class IExportDialogFormButtons(Interface):
    """Export dialog form buttons"""

    download = jsaction.JSButton(title=_("Download"))
    cancel = jsaction.JSButton(title=_("Cancel"))


class ThesaurusExportEditForm(DialogAddForm):
    """Thesaurus export editor"""

    legend = _("Export thesaurus terms")

    layout = getLayoutTemplate()
    parent_interface = IThesaurus

    buttons = button.Buttons(IExportDialogFormButtons)
    fields = field.Fields(IThesaurusExporterConfiguration)

    @property
    def title(self):
        return self.context.title

    @jsaction.handler(buttons['download'])
    def download_handler(self, event, selector):
        return '$.ZTFY.thesaurus.download(this.form);'

    @jsaction.handler(buttons['cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'

    @ajax.handler
    def ajaxDownload(self):
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            writer = getUtility(IJSONWriter)
            return writer.write(self.getAjaxErrors())
        configuration = ThesaurusExporterConfiguration(data)
        exporter = getUtility(IThesaurusExporter, configuration.format)
        return exporter.export(self.getContent(), configuration)

    def create(self, data):
        pass

    def updateContent(self, object, data):
        pass

    def add(self, object):
        pass
