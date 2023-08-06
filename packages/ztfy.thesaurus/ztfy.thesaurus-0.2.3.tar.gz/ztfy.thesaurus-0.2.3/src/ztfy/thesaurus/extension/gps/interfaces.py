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
from zope.interface import Interface

# import local packages

from ztfy.thesaurus import _
from ztfy.utils.schema import DottedDecimalField



class IThesaurusTermGPSExtensionInfo(Interface):
    """Thesaurus term GPS extension info"""

    latitude = DottedDecimalField(title=_("Latitude"),
                                  description=_("GPS latitude value, in WGS84 coordinates system"),
                                  required=True)

    longitude = DottedDecimalField(title=_("Longitude"),
                                   description=_("GPS longitude value, in WGS84 coordinates system"),
                                   required=True)


class IThesaurusTermGPSExtensionTarget(Interface):
    """Thesaurus term GPS extension marker interface"""
