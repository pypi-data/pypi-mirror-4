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
from z3c.form.interfaces import ITextWidget, ISequenceWidget

# import local interfaces

# import Zope3 packages
from zope.interface import Attribute
from zope.schema import TextLine

# import local packages

from ztfy.thesaurus import _


class IThesaurusTermFieldWidget(ITextWidget):
    """Thesaurus term field widget interface"""

    thesaurus_name = TextLine(title=_("Thesaurus name"),
                              required=False,
                              default=u'')

    extract_name = TextLine(title=_("Extract name"),
                            required=False,
                            default=u'')


class IThesaurusTermsListFieldWidget(ISequenceWidget):
    """Thesaurus terms list field widget interface"""

    thesaurus_name = TextLine(title=_("Thesaurus name"),
                              required=False,
                              default=u'')

    extract_name = TextLine(title=_("Extract name"),
                            required=False,
                            default=u'')

    terms = Attribute(_("Widget terms"))
