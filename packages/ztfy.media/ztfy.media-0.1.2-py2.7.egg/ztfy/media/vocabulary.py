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

# import Zope3 interfaces
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ztfy.media.interfaces import IMediaVideoConverter, IMediaAudioConverter

# import Zope3 packages
from zope.component import getUtilitiesFor
from zope.interface import classProvides
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

# import local packages


class VideoConvertersVocabulary(SimpleVocabulary):
    """Video converters vocabulary"""

    classProvides(IVocabularyFactory)

    def __init__(self, context=None):
        terms = [ SimpleTerm(name, name, adapter.label) for name, adapter in getUtilitiesFor(IMediaVideoConverter) ]
        super(VideoConvertersVocabulary, self).__init__(terms)


class AudioConvertersVocabulary(SimpleVocabulary):
    """Video converters vocabulary"""

    classProvides(IVocabularyFactory)

    def __init__(self, context=None):
        terms = [ SimpleTerm(name, name, adapter.label) for name, adapter in getUtilitiesFor(IMediaAudioConverter) ]
        super(AudioConvertersVocabulary, self).__init__(terms)
