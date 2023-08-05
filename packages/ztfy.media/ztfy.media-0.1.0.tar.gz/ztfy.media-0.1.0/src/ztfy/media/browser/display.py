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
import os
import subprocess as sp

# import Zope3 interfaces
from zope.app.file.interfaces import IFile

# import local interfaces
from ztfy.file.interfaces import IImageDisplay

# import Zope3 packages
from zope.app.file.image import Image
from zope.component import adapts
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent
from zope.location import locate

# import local packages
from ztfy.extfile.blob import BlobImage
from ztfy.file.display import ImageDisplayAdapter
from tempfile import NamedTemporaryFile


class VideoMediaDisplayAdapter(ImageDisplayAdapter):
    """Media video display adapter"""

    adapts(IFile)
    implements(IImageDisplay)

    def __new__(cls, context):
        if not context.contentType.startswith('video/'):
            return None
        return ImageDisplayAdapter.__new__(cls, context)

    @property
    def image(self):
        image = self.displays.get('__video__')
        if image is None:
            # We extract image 5 seconds after video starts...
            pipe = sp.Popen(('ffmpeg', '-i', '-', '-ss', '5', '-f', 'image2', '-vframes', '1', '-'),
                            stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
            if pipe:
                stdout, _stderr = pipe.communicate(self.context.data)
                # Some video formats can't be converted via pipes 
                # If we don't get any output we have to use a temporary file
                if not stdout:
                    output = NamedTemporaryFile(prefix='media_', suffix='.img')
                    output.file.write(self.context.data)
                    pipe = sp.Popen(('ffmpeg', '-i', output.name, '-ss', '5', '-f', 'image2', '-vframes', '1', '-'),
                                    stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
                    if pipe:
                        stdout, _stderr = pipe.communicate()
                self.displays['__video__'] = image = BlobImage(stdout)
                notify(ObjectCreatedEvent(image))
                size = image.getImageSize()
                locate(image, self.context, '++display++%dx%d.jpeg' % (size[0], size[1]))
        return image

    def _getVideoSize(self):
        img = self.image
        if img is not None:
            return img.getImageSize()
        else:
            return (-1, -1)

    def getImageSize(self):
        size = self.displays.get('__size__')
        if size is None:
            size = self.displays['__size__'] = self._getVideoSize()
        return size


class AudioMediaDisplayAdapter(ImageDisplayAdapter):
    """Media audio display adapter"""

    adapts(IFile)
    implements(IImageDisplay)

    def __new__(cls, context):
        if not context.contentType.startswith('audio/'):
            return None
        return ImageDisplayAdapter.__new__(cls, context)

    def getDisplay(self, name):
        result = Image(open(os.path.abspath(os.path.join(__file__, '..', 'resources', 'img', 'sound.png'))).read())
        locate(result, self.context, '++display++%s' % name)
        return result
