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

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import Bool, Choice, TextLine

# import local packages
from ztfy.file.schema import FileField
from ztfy.thesaurus.schema import ValidatedChoice
from ztfy.utils.encoding import EncodingField

from ztfy.thesaurus import _


class IThesaurusLoaderConfiguration(Interface):
    """Thesaurus loader configuration interface"""

    name = TextLine(title=_("Thesaurus name"),
                    description=_("Name of the registered thesaurus"),
                    required=True)

    data = FileField(title=_("loader-data-title", "Input data"),
                     description=_("loader-data-description", "Input file containing thesaurus data"),
                     required=True)

    format = Choice(title=_("loader-format-title", "File format"),
                    description=_("loader-format-description", "This list contains available thesauri loaders"),
                    required=True,
                    vocabulary='ZTFY thesaurus loader formats')

    language = Choice(title=_("loader-language-title", "Content language"),
                      description=_("loader-language-description", "Select file language, for formats which don't provide it internally"),
                      required=False,
                      vocabulary='ZTFY base languages')

    encoding = EncodingField(title=_("loader-encoding-title", "File encoding"),
                             description=_("loader-encoding-description", "Select file encoding, for formats which don't provide it internally"),
                             required=False,
                             default='utf-8')


class IThesaurusUpdaterConfiguration(IThesaurusLoaderConfiguration):
    """Thesaurus updater configuration interface"""

    clear = Bool(title=_("updater-clear-title", "Clear before merge ?"),
                 description=_("updater-clear-description", "If 'Yes', thesaurus will be cleared before re-importing file contents"),
                 required=True,
                 default=False)


class IThesaurusLoaderHandler(Interface):
    """Thesaurus loader handler configuration"""

    configuration = Attribute(_("Current handler configuration"))

    def read(self, data, configuration=None):
        """Extract terms from given data"""


class IThesaurusLoader(Interface):
    """Thesaurus loader interface"""

    handler = Attribute(_("Thesaurus handler class"))

    def load(self, data, configuration=None):
        """Load thesaurus from data for the given loader configuration"""


class IThesaurusExporterConfiguration(Interface):
    """Thesaurus exporter configuration interface"""

    filename = TextLine(title=_("export-filename-title", "Export file name"),
                        description=_("export-filename-description", "Full file name, including extension"),
                        required=False)

    format = Choice(title=_("export-format-title", "Export file format"),
                    description=_("export-format-description", "This list contains available thesauri exporters"),
                    required=True,
                    vocabulary="ZTFY thesaurus exporter formats")

    extract = ValidatedChoice(title=_("export-extract-title", "Extract to export"),
                              description=_("export-extract-description", "You can choose to export only an extract of the thesaurus"),
                              required=False,
                              vocabulary="ZTFY thesaurus extracts")


class IThesaurusExporterHandler(Interface):
    """Thesaurus exporter handler configuration"""

    configuration = Attribute(_("Current handler configuration"))

    def write(self, thesaurus, output, configuration=None):
        """Export terms of given thesaurus"""


class IThesaurusExporter(Interface):
    """Thesaurus exporter configuration"""

    handler = Attribute(_("Thesaurus handler class"))

    def export(self, thesaurus, configuration=None):
        """Export thesaurus terms with the given export configuration"""
