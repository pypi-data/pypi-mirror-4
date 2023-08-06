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
from lxml import etree

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.thesaurus.loader import XMLThesaurusLoaderHandler, BaseThesaurusLoader, \
                                  ThesaurusLoaderTerm, ThesaurusLoaderDescription, \
                                  XMLThesaurusExporterHandler, BaseThesaurusExporter
from ztfy.utils.request import queryRequest
from zope.traversing.browser.absoluteurl import absoluteURL


# Namespaces definitions

XML = '{http://www.w3.org/XML/1998/namespace}'
RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
RDFS = '{http://www.w3.org/2000/01/rdf-schema#}'
DC = '{http://purl.org/dc/elements/1.1/}'
DCT = '{http://purl.org/dc/terms/}'
MAP = '{http://www.w3c.rl.ac.uk/2003/11/21-skos-mapping#}'
SKOS = '{http://www.w3.org/2004/02/skos/core#}'


class SKOSThesaurusLoaderHandler(XMLThesaurusLoaderHandler):
    """SKOS format thesaurus handler"""

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
        # check thesaurus scheme
        description = ThesaurusLoaderDescription()
        scheme = root.find('.//' + SKOS + 'ConceptScheme')
        if scheme is not None:
            for element in scheme.getchildren():
                if element.tag == DC + 'title':
                    description.title = unicode(element.text)
                elif element.tag == DC + 'creator':
                    description.creator = unicode(element.text)
                elif element.tag == DC + 'subject':
                    description.subject = unicode(element.text)
                elif element.tag == DC + 'description':
                    description.description = unicode(element.text)
                elif element.tag == DC + 'publisher':
                    description.publisher = unicode(element.text)
                elif element.tag == DC + 'date':
                    description.created = unicode(element.text)
                elif element.tag == DC + 'language':
                    description.language = element.text
        if configuration and not description.language:
            description.language = configuration.language
        # check thesaurus terms
        for concept in root.findall(SKOS + 'Concept'):
            key = concept.attrib.get(RDF + 'about')
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
            for element in concept.getchildren():
                if element.tag == SKOS + 'prefLabel':
                    label = unicode(element.text)
                elif element.tag == SKOS + 'altLabel':
                    term = unicode(element.text)
                    used_for.append(term)
                    terms[term] = ThesaurusLoaderTerm(term, alt=u'', definition=u'', note=u'', generic=u'', specifics=u'',
                                                      associations=u'', usage=key, used_for=[])
                elif element.tag == SKOS + 'definition':
                    definition = unicode(element.text)
                elif element.tag in (SKOS + 'note', SKOS + 'scopeNote'):
                    note = unicode(element.text)
                elif element.tag == SKOS + 'related':
                    associations.append(element.attrib[RDF + 'resource'])
                elif element.tag == SKOS + 'broader':
                    generic = element.attrib[RDF + 'resource']
                elif element.tag == SKOS + 'narrower':
                    specifics.append(element.attrib[RDF + 'resource'])
                elif element.tag == DCT + 'created':
                    created = element.text
            terms[key] = ThesaurusLoaderTerm(label, alt, definition, note, generic, specifics,
                                             associations, usage, used_for, created, modified)
        return description, terms


class SKOSThesaurusLoader(BaseThesaurusLoader):
    """SKOS format thesaurus loader"""

    handler = SKOSThesaurusLoaderHandler


class SKOSThesaurusExporterHandler(XMLThesaurusExporterHandler):
    """SKOS/RDF format thesaurus export handler"""

    def _write(self, thesaurus, configuration=None):
        request = queryRequest()
        thesaurus_url = absoluteURL(thesaurus, request)
        nsmap = { 'rdf': RDF[1:-1],
                  'rdfs': RDFS[1:-1],
                  'dc': DC[1:-1],
                  'dct': DCT[1:-1],
                  'map': MAP[1:-1],
                  'skos': SKOS[1:-1] }
        xml = etree.Element(RDF + 'RDF', nsmap=nsmap)
        doc = etree.ElementTree(xml)
        cs = etree.SubElement(xml, SKOS + 'ConceptScheme')
        cs.attrib[RDF + 'about'] = thesaurus_url
        etree.SubElement(cs, DC + 'title').text = thesaurus.title
        etree.SubElement(cs, DC + 'creator').text = thesaurus.creator
        etree.SubElement(cs, DC + 'subject').text = thesaurus.subject
        etree.SubElement(cs, DC + 'description').text = etree.CDATA(thesaurus.description)
        etree.SubElement(cs, DC + 'publisher').text = thesaurus.publisher
        etree.SubElement(cs, DC + 'date').text = thesaurus.created.strftime('%Y-%m-%d')
        etree.SubElement(cs, DC + 'language').text = thesaurus.language
        extract = configuration and configuration.extract or None
        for term in thesaurus.top_terms:
            if extract and (extract not in (term.extracts or set())):
                continue
            etree.SubElement(cs, SKOS + 'hasTopConcept').attrib[RDF + 'resource'] = absoluteURL(term, request)
        for term in thesaurus.terms.itervalues():
            if extract and (extract not in (term.extracts or set())):
                continue
            concept = etree.SubElement(xml, SKOS + 'Concept')
            concept.attrib[RDF + 'about'] = absoluteURL(term, request)
            sub = etree.SubElement(concept, SKOS + 'prefLabel')
            sub.attrib[XML + 'lang'] = thesaurus.language
            sub.text = term.label
            etree.SubElement(concept, SKOS + 'inScheme').attrib[RDF + 'resource'] = thesaurus_url
            if term.alt:
                sub = etree.SubElement(concept, SKOS + 'altLabel')
                sub.attrib[XML + 'lang'] = thesaurus.language
                sub.text = term.alt
            if term.definition:
                sub = etree.SubElement(concept, SKOS + 'definition')
                sub.attrib[XML + 'lang'] = thesaurus.language
                sub.text = term.definition
            if term.note:
                sub = etree.SubElement(concept, SKOS + 'scopeNote')
                sub.attrib[XML + 'lang'] = thesaurus.language
                sub.text = etree.CDATA(term.note)
            for subterm in term.associations:
                if extract and (extract not in (subterm.extracts or set())):
                    continue
                etree.SubElement(concept, SKOS + 'related').attrib[RDF + 'resource'] = absoluteURL(subterm, request)
            if term.generic:
                etree.SubElement(concept, SKOS + 'broader').attrib[RDF + 'resource'] = absoluteURL(term.generic, request)
            for subterm in term.specifics:
                if extract and (extract not in (subterm.extracts or set())):
                    continue
                etree.SubElement(concept, SKOS + 'narrower').attrib[RDF + 'resource'] = absoluteURL(subterm, request)
            if term.created:
                etree.SubElement(concept, DCT + 'created').text = term.created.strftime('%Y-%m-%d %H:%M:%S')
        return doc


class SKOSThesaurusExporter(BaseThesaurusExporter):
    """SKOS/RDF format thesaurus exporter"""

    handler = SKOSThesaurusExporterHandler
