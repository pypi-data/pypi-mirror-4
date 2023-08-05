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
from ztfy.media.interfaces import IMediaConversionUtility
from ztfy.skin.interfaces import IPropertiesMenuTarget

# import Zope3 packages
from z3c.form import field
from zope.interface import implements

# import local packages
from ztfy.skin.form import EditForm


class MediaConversionUtilityEditForm(EditForm):
    """Media conversion utility edit form"""

    implements(IPropertiesMenuTarget)

    fields = field.Fields(IMediaConversionUtility)
