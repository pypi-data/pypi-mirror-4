from persistent.dict import PersistentDict
from zope import component
from zope import event
from zope import interface
from zope import lifecycleevent
from zope.annotation import interfaces as annointerfaces

from p4a.video import interfaces
from p4a.fileimage import DictProperty

class VideoAnnotationAddedEvent(lifecycleevent.ObjectEvent):
    """Annotations added to an object for video metadata.
    """

class AnnotationVideo(object):
    """An IVideo adapter designed to handle ATCT based file content.
    """

    interface.implements(interfaces.IVideo)

    ANNO_KEY = 'p4a.video.videoanno.AnnotationVideo'

    def __init__(self, context):
        self.context = context
        annotations = annointerfaces.IAnnotations(context)
        self.video_data = annotations.get(self.ANNO_KEY, None)
        if self.video_data is None:
            self.video_data = PersistentDict()
            annotations[self.ANNO_KEY] = self.video_data
            event.notify(VideoAnnotationAddedEvent(self))

    title = DictProperty(interfaces.IVideo['title'], 'video_data')
    description = DictProperty(interfaces.IVideo['description'], 'video_data')
    rich_description = DictProperty(interfaces.IVideo['rich_description'],
                                    'video_data')
    video_author = DictProperty(interfaces.IVideo['video_author'], 'video_data')
    height = DictProperty(interfaces.IVideo['height'], 'video_data')
    width = DictProperty(interfaces.IVideo['width'], 'video_data')
    duration = DictProperty(interfaces.IVideo['duration'], 'video_data')
    file = DictProperty(interfaces.IVideo['file'], 'video_data')
    video_image = DictProperty(interfaces.IVideo['video_image'], 'video_data')
    video_type = DictProperty(interfaces.IVideo['video_type'], 'video_data')
    urls = DictProperty(interfaces.IVideo['urls'], 'video_data')
