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
import chardet
from datetime import datetime
from lxml import etree

# import Zope3 interfaces
from zope.intid.interfaces import IIntIds

# import local interfaces

# import Zope3 packages
from zope.component import getUtility

# import local packages
from ztfy.thesaurus.loader import BaseThesaurusLoader, XMLThesaurusLoaderHandler, \
                                  BaseThesaurusExporter, XMLThesaurusExporterHandler, \
                                  ThesaurusLoaderDescription, ThesaurusLoaderTerm


# namespaces definitions

INM = "{http://www.inmagic.com/webpublisher/query}"


class SuperdocThesaurusLoaderHandler(XMLThesaurusLoaderHandler):
    """SuperDoc format thesaurus load handler"""

    def read(self, data, configuration=None):
        terms = {}
        if configuration is None:
            configuration = self.configuration
        encoding = None
        if configuration and configuration.encoding:
            encoding = configuration.encoding
        if (not encoding) and isinstance(data, (str, unicode)):
            encoding = chardet.detect(data[:1000]).get('encoding', 'utf-8')
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding=encoding)
        xml = etree.parse(data, parser=parser)
        root = xml.getroot()
        # get thesaurus description
        description = ThesaurusLoaderDescription()
        # check thesaurus terms
        for records in root.findall(INM + 'Recordset'):
            for record in records.findall(INM + 'Record'):
                key = None
                label = None
                alt = None
                definition = None
                note = None
                generic = None
                specifics = []
                associations = []
                usage = None
                used_for = []
                created = None
                modified = None
                for element in record.getchildren():
                    if element.text:
                        if element.tag == INM + 'Terme':
                            key = label = unicode(element.text)
                        elif element.tag == INM + 'NA':
                            definition = unicode(element.text)
                        elif element.tag == INM + 'TS':
                            specifics.append(unicode(element.text))
                        elif element.tag == INM + 'TG':
                            generic = unicode(element.text)
                        elif element.tag == INM + 'TA':
                            associations.append(unicode(element.text))
                        elif element.tag == INM + 'EM':
                            usage = unicode(element.text)
                        elif element.tag == INM + 'EP':
                            used_for.append(unicode(element.text))
                        elif element.tag == INM + 'Notes':
                            note = unicode(element.text)
                        elif element.tag == INM + 'DateCreation':
                            created = datetime.strptime(element.text, '%d/%m/%Y')
                        elif element.tag == INM + 'DateModification':
                            modified = datetime.strptime(element.text, '%d/%m/%Y')
                if key:
                    terms[key] = ThesaurusLoaderTerm(label, alt, definition, note, generic, specifics,
                                                     associations, usage, used_for, created, modified)
        return description, terms


class SuperdocThesaurusLoader(BaseThesaurusLoader):
    """SuperDoc export format thesaurus loader"""

    handler = SuperdocThesaurusLoaderHandler



class SuperdocThesaurusExporterHandler(XMLThesaurusExporterHandler):
    """SuperDoc format thesaurus export handler"""

    def _write(self, thesaurus, configuration=None):
        intids = getUtility(IIntIds)
        xml = etree.Element('Results', nsmap={ None: INM[1:-1] },
                            productTitle=u'ONF Thesaurus Manager', productVersion=u'0.1')
        doc = etree.ElementTree(xml)
        extract = configuration and configuration.extract or None
        if extract:
            terms = [ term for term in thesaurus.terms if extract in (term.extracts or set()) ]
        else:
            terms = thesaurus.terms
        rs = etree.SubElement(xml, u'Recordset', setCount=str(len(terms)))
        for index, term in enumerate(thesaurus.terms.itervalues()):
            if extract and (extract not in (term.extracts or set())):
                continue
            rec = etree.SubElement(rs, u'Record', setEntry=str(index))
            etree.SubElement(rec, u'ID').text = str(intids.queryId(term))
            etree.SubElement(rec, u'Terme').text = term.label
            etree.SubElement(rec, u'NA').text = term.note
            added_subterms = False
            if term.specifics:
                for subterm in term.specifics:
                    if extract and (extract not in (subterm.extracts or set())):
                        continue
                    etree.SubElement(rec, u'TS').text = subterm.label
                    added_subterms = True
            if not added_subterms:
                etree.SubElement(rec, u'TS')
            sub = etree.SubElement(rec, u'TG')
            if term.generic:
                sub.text = term.generic.label
            added_subterms = False
            if term.associations:
                for subterm in term.associations:
                    if extract and (extract not in (subterm.extracts or set())):
                        continue
                    etree.SubElement(rec, u'TA').text = subterm.label
                    added_subterms = True
            if not added_subterms:
                etree.SubElement(rec, u'TA')
            sub = etree.SubElement(rec, u'EM')
            if term.usage:
                sub.text = term.usage.label
            added_subterms = False
            if term.used_for:
                for subterm in term.used_for:
                    if extract and (extract not in (subterm.extracts or set())):
                        continue
                    etree.SubElement(rec, u'EP').text = subterm.label
                    added_subterms = True
            if not added_subterms:
                etree.SubElement(rec, u'EP')
            etree.SubElement(rec, u'Notes').text = term.definition
            etree.SubElement(rec, u'Status').text = term.status
            etree.SubElement(rec, u'DateCreation').text = term.created and term.created.strftime('%d/%m/%Y') or u''
            etree.SubElement(rec, u'DateModification').text = term.modified and term.modified.strftime('%d/%m/%Y') or u''
            etree.SubElement(rec, u'Niveau').text = str(term.level)
            etree.SubElement(rec, u'MicroThes').text = term.micro_thesaurus and u'OUI' or u'NON'
            etree.SubElement(rec, u'Terme0').text = (term.parent is None) and term.label or term.parent.label
        return doc


class SuperdocThesaurusExporter(BaseThesaurusExporter):
    """SuperDoc format thesaurus exporter"""

    handler = SuperdocThesaurusExporterHandler
