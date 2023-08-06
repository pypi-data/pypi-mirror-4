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
import atexit
import logging
logger = logging.getLogger('ztfy.media')

import time
import transaction
import zmq

# import Zope3 interfaces
from zope.app.file.interfaces import IFile
from zope.component.interfaces import IRegistered, IUnregistered, ISite
from zope.container.interfaces import IObjectAddedEvent
from zope.processlifetime import IDatabaseOpenedWithRoot
from zope.app.publication.zopepublication import ZopePublication
from zope.traversing import api as traversing_api

# import local interfaces
from ztfy.media.interfaces import IMediaConversionUtility, IMediaInfo, \
                                  CUSTOM_AUDIO_TYPES, CUSTOM_VIDEO_TYPES

# import Zope3 packages
from zope.component import adapter, queryUtility
from zope.site import hooks

# import local packages
from ztfy.media.utility import ConversionMessageHandler, MediasConversionProcess
from ztfy.zmq.process import processExitFunc


_processes = {}


@adapter(IMediaConversionUtility, IRegistered)
def handleRegisteredMediaConversionUtility(utility, event):
    if utility.converter_address:
        path = traversing_api.getPath(utility)
        if _processes.get(path) is None:
            process = MediasConversionProcess(utility.converter_address, ConversionMessageHandler)
            process.start()
            time.sleep(2)
            if process.is_alive():
                _processes[path] = process
                atexit.register(processExitFunc, process=process)
            logger.info("Starting ZMQ listener process %s with PID %d for handler %s" %
                        (process.name, process.pid, str(process.handler)))


@adapter(IMediaConversionUtility, IUnregistered)
def handleUnregisteredMediaConversionUtility(utility, event):
    path = traversing_api.getPath(utility)
    process = _processes.get(path)
    if process is not None:
        process.terminate()
        process.join()
        logger.info("Stopped ZMQ process %s" % process.name)
        del _processes[path]


@adapter(IDatabaseOpenedWithRoot)
def handleOpenedDatabase(event):
    """Launch ZMQ conversion process"""
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    for site in root_folder.values():
        if ISite(site, None) is not None:
            hooks.setSite(site)
            utility = queryUtility(IMediaConversionUtility)
            if (utility is not None) and utility.converter_address:
                try:
                    path = traversing_api.getPath(utility)
                    if _processes.get(path) is None:
                        process = MediasConversionProcess(utility.converter_address, ConversionMessageHandler)
                        process.start()
                        time.sleep(2)
                        if process.is_alive():
                            _processes[path] = process
                            atexit.register(processExitFunc, process=process)
                        logger.info("Starting ZMQ process %s listening on %s with PID %d for handler %s" %
                                    (process.name, utility.converter_address,
                                     process.pid, str(process.handler)))
                except zmq.ZMQError, e:
                    logger.warning("Can't start medias conversion process: " + e.message)


#
# Medias converter after commit hook
#

def checkMediaConversions(status, object):
    if not status:  # transaction aborted
        return
    utility = queryUtility(IMediaConversionUtility)
    if utility is not None:
        utility.checkMediaConversion(object)


@adapter(IFile, IObjectAddedEvent)
def handleNewFile(object, event):
    """Check for conversion of new files"""
    content_type = object.contentType
    if content_type.startswith('audio/') or \
       content_type.startswith('video/') or \
       (content_type in (CUSTOM_AUDIO_TYPES + CUSTOM_VIDEO_TYPES)):
        _infos = IMediaInfo(object)
        transaction.get().addAfterCommitHook(checkMediaConversions, kws={'object': object})
