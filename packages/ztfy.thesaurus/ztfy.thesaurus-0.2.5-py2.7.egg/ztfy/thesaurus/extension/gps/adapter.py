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

# import Zope3 interfaces

# import local interfaces
from ztfy.thesaurus.extension.gps.interfaces import IThesaurusTermGPSExtensionInfo, \
                                                    IThesaurusTermGPSExtensionTarget

# import Zope3 packages
from zope.component import adapter
from zope.interface import implements, implementer
from zope.schema.fieldproperty import FieldProperty
from zope.annotation.interfaces import IAnnotations

# import local packages


class ThesaurusTermGPSExtension(Persistent):
    """Thesaurus term GPS extension"""

    implements(IThesaurusTermGPSExtensionInfo)

    latitude = FieldProperty(IThesaurusTermGPSExtensionInfo['latitude'])
    longitude = FieldProperty(IThesaurusTermGPSExtensionInfo['longitude'])


GPS_EXTENSION_KEY = 'ztfy.thesaurus.extension.gps'

@adapter(IThesaurusTermGPSExtensionTarget)
@implementer(IThesaurusTermGPSExtensionInfo)
def ThesaurusTermGPSExtensionFactory(context):
    """Thesaurus term GPS extension factory"""
    annotations = IAnnotations(context)
    info = annotations.get(GPS_EXTENSION_KEY)
    if info is None:
        info = annotations[GPS_EXTENSION_KEY] = ThesaurusTermGPSExtension()
    return info
