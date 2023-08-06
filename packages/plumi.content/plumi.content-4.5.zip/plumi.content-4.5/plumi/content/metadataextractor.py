#the extract function is ripped from p4a.video

from zope.annotation.interfaces import IAnnotations

from ZODB.PersistentMapping import PersistentMapping

import logging
logger = logging.getLogger('plumi.content')

from hachoir_parser.guess import createParser
from hachoir_metadata.metadata import extractMetadata
from hachoir_core.error import HachoirError
from hachoir_core.stream import InputStreamError

def extract(filename):
    """Extract the metadata from the media file"""

    filename = unicode(filename)

    try:
        parser = createParser(filename)
    except InputStreamError, err:
        logger.error("stream error! %s\n" % unicode(err))
        return None

    if not parser:
        logger.info("Unable to create parser.\n")
        return None
    try:
        metadata = extractMetadata(parser)
    except HachoirError, err:
        logger.info("empty stream! %s\n" % unicode(err))
        return None

    if metadata is None:
        logger.info("unable to extract metadata.\n")
        return None

    return metadata

def setup_metadata(obj):
    annotations = IAnnotations(obj, None)
    if not annotations.has_key('plumi.video_info'):
        annotations['plumi.video_info'] = PersistentMapping()
    video_info = annotations.get('plumi.video_info')

    filename = obj.video_file.getBlob().committed()
    if not filename:
        return

    metadata = extract(filename)
    try:
        video_info['width'] = metadata.get('width')
        video_info['height'] = metadata.get('height')
        video_info['aspect_ratio'] = video_info['width']/video_info['height']
    except (ValueError, AttributeError):
        logger.info('Could not get video dimensions')
    try:
        video_info['duration'] = metadata.get('duration')
    except (ValueError, AttributeError):
        logger.info('Could not get video duration')
