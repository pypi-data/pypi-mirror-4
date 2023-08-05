import mimetypes
import os
from zope import interface
from zope.annotation import interfaces as annointerfaces
from OFS import Image as ofsimage

from p4a.video import interfaces
from p4a.fileimage import utils as fileutils
from p4a.video import metadataextractor


def write_video_image(id3tags, video_image):
    size = video_image.get_size()
    mime_type = video_image.content_type
    desc = u''

    tempfilename = fileutils.write_to_tempfile(video_image)
    frame = frames.ImageFrame.create(frames.ImageFrame.FRONT_COVER,
                                     tempfilename,
                                     desc)

    imgs = id3tags.getImages()
    if len(imgs) == 0:
        id3tags.frames.append(frame)
    else:
        # find the frame index of the first image so we can
        # replace it with our new image frame
        for i in id3tags.frames:
            if i == imgs[0]:
                index = id3tags.frames.index(i)
                id3tags.frames[index] = frame
                break

class RealVideoDataAccessor(object):
    interface.implements(interfaces.IVideoDataAccessor)

    def __init__(self, context):
        self._filecontent = context

    @property
    def video_type(self):
        return 'RAM'

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

    def load(self, filename):
        # TODO: need to verify height is extracted properly (db)
        metadata = metadataextractor.extract(filename)
        self._video_data['height'] = getattr(metadata,'height',[None])[0]
        self._video_data['width'] = getattr(metadata,'width',[None])[0]
        self._video_data['duration'] = getattr(metadata,'duration',[None])[0]

    def store(self, filename):
        # content_type = self._filecontent.get_content_type()
        pass
