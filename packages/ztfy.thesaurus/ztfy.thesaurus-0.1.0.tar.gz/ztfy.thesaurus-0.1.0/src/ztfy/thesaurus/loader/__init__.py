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
from BTrees.OOBTree import OOBTree
from datetime import datetime
from tempfile import TemporaryFile

# import Zope3 interfaces

# import local interfaces
from ztfy.thesaurus.interfaces.loader import IThesaurusLoader, IThesaurusLoaderHandler, \
                                             IThesaurusExporter, IThesaurusExporterHandler
from ztfy.thesaurus.interfaces.thesaurus import IThesaurusInfoBase

# import Zope3 packages
from zope.interface import implements
from zope.publisher.browser import FileUpload
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.thesaurus.term import ThesaurusTerm
from ztfy.thesaurus.thesaurus import Thesaurus, ThesaurusTermsContainer
from ztfy.utils.request import getRequest


class ThesaurusLoaderDescription(object):
    """Thesaurus loader description"""

    implements(IThesaurusInfoBase)

    title = FieldProperty(IThesaurusInfoBase['title'])
    subject = FieldProperty(IThesaurusInfoBase['subject'])
    description = FieldProperty(IThesaurusInfoBase['description'])
    creator = FieldProperty(IThesaurusInfoBase['creator'])
    publisher = FieldProperty(IThesaurusInfoBase['publisher'])
    _created = FieldProperty(IThesaurusInfoBase['created'])
    language = FieldProperty(IThesaurusInfoBase['language'])

    @property
    def created(self):
        return self._created

    @created.setter
    def created(self, value):
        if isinstance(value, (str, unicode)):
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                value = datetime.today().date()
        self._created = value


class ThesaurusLoaderTerm(object):
    """Base thesaurus loader term"""

    def __init__(self, label, alt=None, definition=None, note=None, generic=None, specifics=[],
                 associations=[], usage=None, used_for=[], created=None, modified=None):
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


class BaseThesaurusLoaderHandler(object):
    """Base thesaurus loader handler"""

    implements(IThesaurusLoaderHandler)

    def __init__(self, configuration):
        self.configuration = configuration


class XMLThesaurusLoaderHandler(BaseThesaurusLoaderHandler):
    """Base XML thesaurus loader handler"""


class BaseThesaurusLoader(object):
    """Base thesaurus loader"""

    implements(IThesaurusLoader)

    handler = None

    def load(self, data, configuration=None):
        handler = self.handler(configuration)
        if isinstance(data, tuple):
            data = data[0]
        if isinstance(data, (file, FileUpload)):
            data.seek(0)
        description, terms = handler.read(data)
        key_store = OOBTree()
        store = ThesaurusTermsContainer()
        # first loop to initialize terms
        for key, term in terms.iteritems():
            key_store[key] = store[term.label] = ThesaurusTerm(label=term.label, alt=term.alt, definition=term.definition, note=term.note,
                                                               created=term.created, modified=term.modified)
        # second loop to update terms links
        for key, term in terms.iteritems():
            new_term = key_store[key]
            if term.generic:
                new_term.generic = key_store.get(term.generic)
            if term.specifics:
                new_term.specifics = [key_store.get(specific) for specific in term.specifics]
            if term.associations:
                new_term.associations = [key_store.get(association) for association in term.associations]
            if term.usage:
                new_term.usage = key_store.get(term.usage)
            if term.used_for:
                new_term.used_for = [key_store.get(used) for used in term.used_for]
        return Thesaurus(description=description, terms=store)


class BaseThesaurusExporterHandler(object):
    """Base thesaurus exporter handler"""

    implements(IThesaurusExporterHandler)

    def __init__(self, configuration):
        self.configuration = configuration


class XMLThesaurusExporterHandler(BaseThesaurusExporterHandler):
    """Base XML thesaurus export handler"""

    def _write(self, thesaurus, configuration=None):
        raise NotImplementedError

    def write(self, thesaurus, output, configuration=None):
        doc = self._write(thesaurus, configuration)
        doc.write(output, encoding='utf-8', xml_declaration=True, standalone=True, pretty_print=True)
        return { 'Content-Type': 'text/xml; encoding=utf-8' }


class BaseThesaurusExporter(object):
    """Base thesaurus exporter"""

    implements(IThesaurusExporter)

    handler = None

    def export(self, thesaurus, configuration=None):
        handler = self.handler(configuration)
        output = TemporaryFile()
        result = handler.write(thesaurus, output, configuration)
        request = getRequest()
        if request is not None:
            request.response.setHeader('Content-Type', result.get('Content-Type', 'text/plain'))
            filename = configuration.filename
            if not filename:
                filename = thesaurus.name + '.xml'
            request.response.setHeader('Content-Disposition', 'attachment; filename="%s"' % filename)
        return output
