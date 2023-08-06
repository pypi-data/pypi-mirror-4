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

# import local packages

from ztfy.thesaurus import _


class INode(Interface):
    """Tree node interface"""

    context = Attribute(_("Node's context"))

    label = Attribute(_("Node's label"))

    cssClass = Attribute(_("Node's CSS class"))

    def getLevel(self):
        """Get depth level of current node"""

    def hasChildren(self):
        """Check if current node has childrens"""

    def getChildren(self):
        """Get list of node childrens"""


class ITree(Interface):
    """Tree interface"""

    def getRootNodes(self):
        """Get list of root nodes"""
