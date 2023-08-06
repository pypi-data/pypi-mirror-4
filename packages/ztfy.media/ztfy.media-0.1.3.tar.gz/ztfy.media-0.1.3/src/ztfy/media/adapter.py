### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages
import mimetypes
from BTrees.OOBTree import OOBTree
from persistent.dict import PersistentDict

# import Zope3 interfaces
from zope.app.file.interfaces import IFile
from zope.annotation.interfaces import IAnnotations
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.media.interfaces import IMediaInfo, IMediaConversions, \
                                  CUSTOM_AUDIO_TYPES, CUSTOM_VIDEO_TYPES

# import Zope3 packages
from zope.component import adapts
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent
from zope.location import locate
from zope.traversing import namespace

# import local packages
from ztfy.extfile.blob import BlobFile
from ztfy.media.ffbase import FFmpeg


#
# Media infos
#

MEDIA_INFOS_KEY = 'ztfy.media.infos'

class MediaInfosAdapter(object):
    """Media infos adapter"""

    adapts(IFile)
    implements(IMediaInfo)

    def __new__(self, context):
        if not (context.contentType.startswith('audio/') or
                context.contentType.startswith('video/') or
                (context.contentType in (CUSTOM_AUDIO_TYPES + CUSTOM_VIDEO_TYPES))):
            return None
        return object.__new__(self, context)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        infos = annotations.get(MEDIA_INFOS_KEY)
        if infos is None:
            infos = FFmpeg().info(self.context)
            if infos:
                infos = annotations[MEDIA_INFOS_KEY] = PersistentDict(infos[0])
            else:
                infos = annotations[MEDIA_INFOS_KEY] = {}
        self.infos = infos


#
# Media conversions
#

MEDIA_CONVERSIONS_KEY = 'ztfy.media.conversions'

class MediaConversionsAdapter(object):
    """Media conversions adapter"""

    adapts(IFile)
    implements(IMediaConversions)

    def __new__(self, context):
        if not (context.contentType.startswith('audio/') or
                context.contentType.startswith('video/') or
                (context.contentType in (CUSTOM_AUDIO_TYPES + CUSTOM_VIDEO_TYPES))):
            return None
        return object.__new__(self, context)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        conversions = annotations.get(MEDIA_CONVERSIONS_KEY)
        if conversions is None:
            # Use OOBTree to reduce conflicts when converting to several
            # formats simultaneously...
            conversions = annotations[MEDIA_CONVERSIONS_KEY] = OOBTree()
        self.conversions = conversions

    def addConversion(self, data, format, extension=None, width=None):
        target = BlobFile()
        notify(ObjectCreatedEvent(target))
        target.data = data
        target.contentType = format
        if extension is None:
            extension = mimetypes.guess_extension(format)
        target_name = '%s%s' % (('w%d' % width) if width else 'media', extension)
        self.conversions[target_name] = target
        target_name = '++conversion++%s' % target_name
        locate(target, self.context, target_name)

    def hasConversion(self, formats):
        if self.context.contentType in formats:
            return True
        for conversion in self.getConversions():
            if conversion.contentType in formats:
                return True
        return False

    def getConversions(self):
        return [self.context] + list(self.conversions.values())

    def getConversion(self, name):
        if '/' in name:
            for conversion in self.getConversions():
                if conversion.contentType == name:
                    return conversion
        return self.conversions.get(name)


class MediaConversionPathTraverser(namespace.view):
    """Media ++conversion++ traverse adapter"""

    def traverse(self, name, ignored):
        conversions = IMediaConversions(self.context, None)
        if conversions is not None:
            result = conversions.getConversion(name)
            if result is not None:
                return result
        raise TraversalError("++conversion++%s" % name)
