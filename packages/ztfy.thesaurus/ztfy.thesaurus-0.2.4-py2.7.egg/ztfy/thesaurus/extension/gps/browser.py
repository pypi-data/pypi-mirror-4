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
from ztfy.thesaurus.extension.gps.interfaces import IThesaurusTermGPSExtensionInfo

# import local interfaces

# import Zope3 packages
from z3c.form import field

# import local packages
from ztfy.skin.form import DialogEditForm

from ztfy.thesaurus import _



class ThesaurusTermGPSEditDialog(DialogEditForm):
    """Thesaurus term GPS extension info edit form"""

    @property
    def title(self):
        return self.getContent().label

    legend = _("Update GPS coordinates")

    fields = field.Fields(IThesaurusTermGPSExtensionInfo)
