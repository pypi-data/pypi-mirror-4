# -*- coding: utf-8 -*-
from zope import interface
from zope.annotation import interfaces as annointerfaces

from p4a.video import interfaces
from p4a.video import metadataextractor

DEFAULT_CHARSET = 'utf-8'

def td_to_seconds(td):
    """
    """

    total = td.days * 24 * 60 * 60
    total += td.seconds
    total = float(total) + (float(td.microseconds) * 0.000001)

    return total

def unicodestr(v, charset=DEFAULT_CHARSET):
    """Return the unicode object representing the value passed in an
    as error-immune manner as possible.

      >>> unicodestr(u'foo')
      u'foo'
      >>> unicodestr('bar')
      u'bar'
      >>> unicodestr('héllo wórld', 'ascii')
      u'h\\ufffd\\ufffdllo w\\ufffd\\ufffdrld'
    """

    if isinstance(v, unicode):
        return v
    if isinstance(v, str):
        return v.decode(charset, 'replace')
    return unicode(v)

MISSING = [None]

class AbstractDataAccessor(object):
    interface.implements(interfaces.IVideoDataAccessor)

    def __init__(self, context):
        self._filecontent = context

    @property
    def _video(self):
        video = getattr(self, '__cached_video', None)
        if video is not None:
            return video
        self.__cached_video = interfaces.IVideo(self._filecontent)
        return self.__cached_video

    @property
    def _video_data(self):
        annotations = annointerfaces.IAnnotations(self._filecontent)
        return annotations.get(self._video.ANNO_KEY, None)

    def _setup_data(self, metadata, attr, convert_func):
        try:
            data = metadata.getItems(attr)
        except ValueError, e:
            # no valid data
            return

        if len(data) >= 1:
            self._video_data[attr] = convert_func(data[0].value)
        else:
            self._video_data[attr] = interfaces.IVideo[attr].default

    def load(self, filename):
        metadata = metadataextractor.extract(filename)
        if metadata is not None:
            self._setup_data(metadata, 'height', int)
            self._setup_data(metadata, 'width', int)
            self._setup_data(metadata, 'duration', td_to_seconds)

    def store(self, filename):
        raise NotImplementedError('Write support not yet implemented')
