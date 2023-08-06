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
from zope.app.file.interfaces import IFile
from zope.browser.interfaces import IBrowserView
from zope.pagetemplate.interfaces import IPageTemplate

# import local interfaces
from ztfy.file.interfaces import IImageDisplay
from ztfy.media.interfaces import IMediaConversions, CUSTOM_VIDEO_TYPES, CUSTOM_AUDIO_TYPES
from ztfy.media.browser.interfaces import IMediaPreview
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.template.template import getPageTemplate
from zope.component import adapter, adapts, getMultiAdapter, queryAdapter, queryMultiAdapter
from zope.interface import implementer, implements

# import local packages
from ztfy.skin.page import BaseTemplateBasedPage


DEFAULT_VIDEO_WIDTH = 700


class BaseMediaPreviewAdapter(object):
    """Base media preview adapter"""

    adapts(IFile, IZTFYBrowserLayer)
    implements(IMediaPreview)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        self.conversions = IMediaConversions(self.context)

    template = getPageTemplate()

    def render(self):
        if self.template is None:
            template = getMultiAdapter((self, self.request), IPageTemplate)
            return template(self)
        return self.template()


class VideoPreviewAdapter(BaseMediaPreviewAdapter):
    """Video preview adapter"""

    def __new__(cls, context, request):
        if not (context.contentType.startswith('video/') or
                (context.contentType in CUSTOM_VIDEO_TYPES)):
            return None
        return BaseMediaPreviewAdapter.__new__(cls, context, request)

    @property
    def size(self):
        display = queryAdapter(self.context, IImageDisplay, name='video')
        if display is not None:
            width, height = display.getImageSize()
            return (DEFAULT_VIDEO_WIDTH, int(1. * DEFAULT_VIDEO_WIDTH * height / width))
        else:
            return (DEFAULT_VIDEO_WIDTH, 500)


class AudioPreviewAdapter(BaseMediaPreviewAdapter):
    """Audio preview adapter"""

    def __new__(cls, context, request):
        if not (context.contentType.startswith('audio/') or
                (context.contentType in CUSTOM_AUDIO_TYPES)):
            return None
        return BaseMediaPreviewAdapter.__new__(cls, context, request)



class MediaView(BaseTemplateBasedPage):
    """Media view"""

    def __init__(self, context, request, preview):
        BaseTemplateBasedPage.__init__(self, context, request)
        self.preview = preview

    def update(self):
        super(MediaView, self).update()
        self.preview.update()


@adapter(IFile, IZTFYBrowserLayer)
@implementer(IBrowserView)
def MediaViewFactory(context, request):
    if context.contentType.startswith('audio/') or context.contentType in CUSTOM_AUDIO_TYPES:
        preview = queryMultiAdapter((context, request), IMediaPreview, name='audio')
    elif context.contentType.startswith('video/') or context.contentType in CUSTOM_VIDEO_TYPES:
        preview = queryMultiAdapter((context, request), IMediaPreview, name='video')
    else:
        preview = None
    if preview is None:
        return None
    return MediaView(context, request, preview)
