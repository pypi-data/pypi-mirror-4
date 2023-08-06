.. contents::

Introduction
============

ztfy.media is a ZTK/ZopeApp ZTFY package used to automatically convert and display
medias files (audios, videos...).

It was developed in the context of a medias library management application handling several
kinds of medias (mainly images, videos, and audio files), to be able to automatically display
these contents in web pages.


Medias conversions
==================

Automatic medias conversions implies several pre-requisites:

 - the ''ffmpeg'' executable must be available in your path;

 - you have to rely on a ZEO connection handling a blobs cache directory;

 - you have to create and register (with a name) this ZEO connection in your site management folder
   (see ztfy.utils.zodb.ZEOConnection object);

 - you have to create and register (without name) a ZTFY medias conversion utility.

Medias conversion utility allows you to define listening address and port of a ZeroMQ process which
will wait for conversions requests. These requests are automatically done when an IObjectAddedEvent
is notified on a IFile object containing contents for which a converter has been registered; default
converters based on FFmpeg are available for images, video and audio files, but you can provide your
own converters for any kind of custom file.

Medias conversion utility also allows to define in which formats you want to convert the new medias.
All conversions are actually done with the help of FFmpeg, each conversion being done in a dedicated
sub-process handling it's own ZEO connection.

Converted medias are stored in the ZODB as Blob files in the original media file annotations.
