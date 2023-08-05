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
import logging
logger = logging.getLogger('ztfy.media')

from multiprocessing.process import Process
from persistent import Persistent
from threading import Thread
import os
import zmq

# import Zope3 interfaces
from transaction.interfaces import ITransactionManager
from zope.app.file.interfaces import IFile
from zope.component.interfaces import ISite
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.media.interfaces import IMediaConversionUtility, IMediaConversions, IMediaConverter, \
                                  CUSTOM_AUDIO_TYPES, CUSTOM_VIDEO_TYPES
from ztfy.utils.interfaces import IZEOConnection

# import Zope3 packages
from zope.app.publication.zopepublication import ZopePublication
from zope.component import getUtility, queryUtility, hooks
from zope.container.contained import Contained
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.traversing import api as traversing_api

# import local packages
from ztfy.utils.request import getRequest, newParticipation, endParticipation
from ztfy.utils.traversing import getParent
from ztfy.utils.zodb import ZEOConnectionInfo
from ztfy.zmq.handler import ZMQMessageHandler
from ztfy.zmq.process import ZMQProcess


#
# Media conversion process
#

class MediasConversionProcess(ZMQProcess):
    """Medias conversion process"""


class ConversionProcess(Process):
    """Conversion manager process"""

    def __init__(self, settings, group=None, target=None, name=None, *args, **kwargs):
        Process.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs)
        self.settings = settings

    def run(self):
        # Lower process nice to keep web interface responsive
        os.nice(10)
        settings = self.settings
        zeo_settings = settings.get('zeo')
        media_path = settings.get('media')
        media_format = settings.get('format')
        if not (zeo_settings and media_path and media_format):
            logger.warning("Received bad conversion request: %s" % str(settings))
            return
        logger.info("Received media conversion request: %s => %s" % (media_path, media_format))
        connection_info = ZEOConnectionInfo()
        connection_info.update(zeo_settings)
        newParticipation(settings.get('principal'))
        request = getRequest()
        root = None
        manager = None
        storage, db = connection_info.getConnection(get_storage=True)
        try:
            connection = db.open()
            root = connection.root()
            root_folder = root.get(ZopePublication.root_name, None)
            media = traversing_api.traverse(root_folder, media_path, default=None, request=request)
            if IFile.providedBy(media):
                site = getParent(media, ISite)
                hooks.setSite(site)
                manager = ITransactionManager(media)
                converter = queryUtility(IMediaConverter, media_format)
                if converter is not None:
                    # extract converter output
                    conversion = converter.convert(media)
                    # add conversion in a transaction attempts loop
                    for attempt in manager.attempts():
                        with attempt as t:
                            IMediaConversions(media).addConversion(conversion, media_format, '.%s' % converter.format)
                        if t.status == 'Committed':
                            break
                else:
                    logger.warning("Can't find requested converter: %s" % media_format)
            else:
                logger.warning("Can't find requested media: %s" % media_path)
        finally:
            endParticipation()
            if manager is not None:
                manager.abort()
            connection.close()
            storage.close()


#
# Medias conversion handlers
#

class ConversionThread(Thread):

    def __init__(self, process):
        Thread.__init__(self)
        self.process = process

    def run(self):
        self.process.start()
        self.process.join()


class ConversionHandler(object):
    """Media conversion manager
    
    The conversion manager is launched by a ZMQ 'convert' JSON message, which
    should contain the following attributes:
     - zeo: dict of ZEO connection settings
     - media: complete path to the new media
     - format: requested conversion format
    """

    def convert(self, data):
        ConversionThread(ConversionProcess(data)).start()
        return [ 200, 'OK - Conversion process started' ]


class ConversionMessageHandler(ZMQMessageHandler):
    """Media conversion message handler"""

    handler = ConversionHandler


#
# Medias conversion configuration utility
#


class MediaConversionUtility(Persistent, Contained):
    """Media conversion configuration utility"""

    implements(IMediaConversionUtility)

    converter_address = FieldProperty(IMediaConversionUtility['converter_address'])
    video_formats = FieldProperty(IMediaConversionUtility['video_formats'])
    audio_formats = FieldProperty(IMediaConversionUtility['audio_formats'])
    zeo_connection = FieldProperty(IMediaConversionUtility['zeo_connection'])

    def checkMediaConversion(self, media):
        """Request conversion of given media"""
        content_type = media.contentType
        if (content_type.startswith('audio/') or
            (content_type in CUSTOM_AUDIO_TYPES)) and self.audio_formats:
            requested_formats = [ format for format in self.audio_formats if format != content_type ]
        elif (content_type.startswith('video/') or
              (content_type in CUSTOM_VIDEO_TYPES)) and self.video_formats:
            requested_formats = [ format for format in self.video_formats if format != content_type ]
        for format in requested_formats:
            self.convert(media, format)

    def convert(self, media, format):
        """Send conversion request for given media"""
        if not self.zeo_connection:
            return
        zeo = getUtility(IZEOConnection, self.zeo_connection)
        settings = { 'zeo': zeo.getSettings(),
                     'principal': IZopeDublinCore(media).creators[0],
                     'media': traversing_api.getPath(media),
                     'format': format }
        request = [ 'convert', settings ]
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect('tcp://' + self.converter_address)
        socket.send_json(request)
        return socket.recv_json()
