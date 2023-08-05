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
from zope.schema import TextLine, URI

# import local packages

from ztfy.thesaurus import _


class IThesaurusTermExtension(Interface):
    """Thesaurus term extension interface
    
    An extension is a marker interface implemented by
    a term, which provides additional attributes to the term.
    
    Each available extension is defined as a named utility.
    """

    label = TextLine(title=_("Extension name"),
                     description=_("User name given to the extension"),
                     required=True)

    target_interface = Attribute(_("Extension marker interface"))

    target_view = URI(title=_("Extension target view"),
                      required=True)

    icon = URI(title=_("Extension icon URI"),
               required=True)
