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
from fanstatic import Library, Resource

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.blog.browser import ztfy_blog_back
from ztfy.jqueryui import jquery_alerts, jquery_jsonrpc


library = Library('ztfy.thesaurus', 'resources')

ztfy_thesaurus_css = Resource(library, 'css/ztfy.thesaurus.css')

ztfy_thesaurus = Resource(library, 'js/ztfy.thesaurus.js',
                          minified='js/ztfy.thesaurus.min.js',
                          depends=[ztfy_blog_back, jquery_alerts, jquery_jsonrpc,
                                   ztfy_thesaurus_css])
