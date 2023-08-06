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
from ztfy.thesaurus.extension.gps.interfaces import IThesaurusTermGPSExtensionTarget
from ztfy.thesaurus.interfaces.extension import IThesaurusTermExtension

# import Zope3 packages
from zope.interface import implements

# import local packages

from ztfy.thesaurus import _


class ThesaurusTermGPSExtension(object):
    """Thesaurus term GPS extension"""

    implements(IThesaurusTermExtension)

    label = _("GPS coordinates")
    target_interface = IThesaurusTermGPSExtensionTarget
    target_view = "@@gps.html"
    icon = '/--static--/ztfy.thesaurus/img/gps.png'
