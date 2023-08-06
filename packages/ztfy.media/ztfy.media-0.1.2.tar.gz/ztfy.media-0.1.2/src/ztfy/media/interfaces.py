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
from zope.schema import TextLine, Choice, List

# import local packages

from ztfy.media import _


#
# Medias interfaces
#

CUSTOM_AUDIO_TYPES = ('application/ogg',)
CUSTOM_VIDEO_TYPES = ()


class IMediaInfo(Interface):
    """Media file info interface"""

    vtype = Attribute(_("Media type"))

    audio_codec_name = Attribute(_("Media audio codec name"))

    video_codec_name = Attribute(_("Media video codec name"))

    duration = Attribute(_("Media duration, in seconds"))

    bitrate = Attribute(_("Media audio bitrate"))

    frame_rate = Attribute(_("Media video frames rate"))

    frame_size = Attribute(_("Media frame size, if available"))

    frame_mode = Attribute(_("Media frame mode, if available"))

    infos = Attribute(_("Complete media infos dictionary"))


#
# Media converter utility interfaces
#

class IMediaConverter(Interface):
    """Media converter interface"""

    label = Attribute(_("Media converter label"))

    format = Attribute(_("Media converter target format"))

    def convert(self, media):
        """Convert media to format handled by given converter"""


class IMediaVideoConverter(IMediaConverter):
    """Media video converter"""


class IMediaAudioConverter(IMediaConverter):
    """Media audio converter"""


#
# Media conversions adapter interfaces
#

class IMediaConversionsInfo(Interface):
    """Media conversions info interface"""

    def hasConversion(self, formats):
        """Check if one of given formats if available in conversions"""

    def getConversion(self, format):
        """Get converted media for given format and width"""

    def getConversions(self):
        """Get current list of media conversions"""


class IMediaConversionsWriter(Interface):
    """Media conversions writer interface"""

    def addConversion(self, conversion, format, extension=None, width=None):
        """Add given conversion to media"""


class IMediaConversions(IMediaConversionsInfo, IMediaConversionsWriter):
    """Media file conversions storage interface"""


#
# Media conversion utility configuration interface
#

class IMediaConversionUtility(Interface):
    """Media conversion client interface"""

    converter_address = TextLine(title=_("Medias converter process address"),
                                 description=_("""Address of media converter listener, in the 'IPv4:port' format."""
                                               """Keep empty to disable it."""),
                                 required=False,
                                 default=u'127.0.0.1:5555')

    video_formats = List(title=_("Video formats conversions"),
                         description=_("Published video files will be automatically converted to this format"),
                         value_type=Choice(vocabulary="ZTFY media video converters"))

    audio_formats = List(title=_("Audio formats conversions"),
                         description=_("Published audio files will be automatically converted to this format"),
                         value_type=Choice(vocabulary="ZTFY media audio converters"))

    zeo_connection = Choice(title=_("ZEO connection name"),
                            description=_("Name of ZEO connection utility defining converter connection"),
                            required=True,
                            vocabulary="ZEO connections")

    def checkMediaConversion(self, media):
        """Check if conversion is needed for given media"""

    def convert(self, media, format):
        """Convert given media to requested format"""
