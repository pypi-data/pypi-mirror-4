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
from ztfy.jqueryui import jquery

library = Library('ztfy.media', 'resources')


# FlowPlayer resource
flowplayer = Resource(library, 'js/flowplayer-3.2.11.min.js', depends=[jquery])


# ztfy.media resources
ztfy_media_css = Resource(library, 'css/ztfy.media.css', minified='css/ztfy.media.min.css')

ztfy_video = Resource(library, 'js/ztfy.media.js', minified='js/ztfy.media.min.js',
                      depends=[jquery], bottom=True)
