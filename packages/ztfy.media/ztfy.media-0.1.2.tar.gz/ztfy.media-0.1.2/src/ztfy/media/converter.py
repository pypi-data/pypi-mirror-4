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
from cStringIO import StringIO
from tempfile import NamedTemporaryFile

# import Zope3 interfaces

# import local interfaces
from ztfy.media.interfaces import IMediaAudioConverter, IMediaVideoConverter

# import Zope3 packages
from zope.interface import implements

# import local packages
from ztfy.media.ffbase import INPUT_BLOCK_SIZE
from ztfy.media.ffdocument import FFDocument

from ztfy.media import _


class BaseMediaConverter(object):
    """Base media converter"""

    require_temp_file = False

    def convert(self, media):
        """Convert media"""
        if isinstance(media, (str, unicode)):
            media = StringIO(media)
        document = FFDocument(media)
        self.addFilters(document)
        if self.require_temp_file:
            output = NamedTemporaryFile(bufsize=INPUT_BLOCK_SIZE, prefix='media_', suffix='.%s' % self.format)
            document.getOutput(self.format, target=output.name)
            output.file.seek(0)
            return output.file.read()
        else:
            return document.getOutput(self.format)

    def addFilters(self, document):
        pass


class WavAudioConverter(BaseMediaConverter):
    """Default WAV media converter"""

    implements(IMediaAudioConverter)

    label = _("WAV audio converter")
    format = 'wav'


class Mp3AudioConverter(BaseMediaConverter):
    """Default MP3 media converter"""

    implements(IMediaAudioConverter)

    label = _("MP3 audio converter")
    format = 'mp3'


class OggAudioConverter(BaseMediaConverter):
    """Default OGG audio converter"""

    implements(IMediaAudioConverter)

    label = _("OGG audio converter")
    format = 'ogg'


class FlvVideoConverter(BaseMediaConverter):
    """Default FLV media converter"""

    implements(IMediaVideoConverter)

    label = _("FLV (Flash Video) video converter")
    format = 'flv'

    def addFilters(self, document):
        document.audiosampling(22050)
        document.bitrate(1200)
        document.size('4cif')


class Mp4VideoConverter(BaseMediaConverter):
    """Default MP4 media converter"""

    implements(IMediaVideoConverter)

    label = _("MP4 (HTML5) video converter")
    format = 'mp4'
    require_temp_file = True

    def addFilters(self, document):
        document.audiosampling(22050)
        document.bitrate(1200)
        document.size('4cif')


class OggVideoConverter(BaseMediaConverter):
    """OGG media converter"""

    implements(IMediaVideoConverter)

    label = _("OGG video converter")
    format = 'ogg'

    def addFilters(self, document):
        document.audiosampling(22050)
        document.bitrate(1200)
        document.size('4cif')


class WebmVideoConverter(BaseMediaConverter):
    """WebM Media converter"""

    implements(IMediaVideoConverter)

    label = _("WebM video converter")
    format = 'webm'

    def addFilters(self, document):
        document.audiosampling(22050)
        document.bitrate(1200)
        document.size('4cif')
