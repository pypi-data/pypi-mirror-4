from zope import interface
from zope import schema
from p4a.fileimage import file as p4afile
from p4a.fileimage import image as p4aimage
from p4a.video import genre

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('p4a.video')


class IAnyVideoCapable(interface.Interface):
    """Any aspect of video/content capable.
    """

class IPossibleVideo(IAnyVideoCapable):
    """All objects that should have the ability to be converted to some
    form of video should implement this interface.
    """

class IVideoEnhanced(interface.Interface):
    """All objects that have their media features activated/enhanced
    should have this marker interface applied.
    """

class IVideo(interface.Interface):
    """Objects which have video information.
    """

    title = schema.TextLine(title=_(u'Title'), required=False)
    description = schema.Text(title=_(u'Description'), required=False)
    rich_description = schema.Text(title=_(u'Rich Text Description'),
                                   required=False)
    file = p4afile.FileField(title=_(u'File'), required=False)
    width = schema.Int(title=_(u'Width'), default=480, required=False,
                       readonly=False)
    height = schema.Int(title=_(u'Height'), default=360, required=False,
                        readonly=False)
    duration = schema.Float(title=_(u'Duration'), required=False, readonly=False)

    video_image = p4aimage.ImageField(title=_(u'Image'), required=False,
                                      preferred_dimensions=(320, 240))

    video_type = schema.TextLine(title=_(u'Type'),
                                 required=True,
                                 readonly=True)

    video_author = schema.TextLine(title=_(u'Author'), required=False)

    urls = schema.Tuple(
        title=_(u'Video URLs'), required=False, default=(),
        value_type=schema.Tuple(title=_(u'Mimetype and URL pair'),
                                min_length=2, max_length=2))

class IVideoDataAccessor(interface.Interface):
    """Video implementation accessor (ie mov, wma, flv).
    """

    video_type = schema.TextLine(title=_(u'Video Type'),
                                 required=True,
                                 readonly=True)

    def load(filename):
        pass
    def store(filename):
        pass

class IMediaPlayer(interface.Interface):
    """Media player represented as HTML.
    """

    def __call__(downloadurl, imageurl):
        """Return the HTML required to play the video content located
        at *downloadurl* with the *imageurl* representing the video.
        """

class IPossibleVideoContainer(IAnyVideoCapable):
    """Any folderish entity tha can be turned into an actual video 
    container.
    """

class IVideoContainerEnhanced(interface.Interface):
    """Any folderish entity that has had it's IVideoContainer features
    enabled.
    """

class IVideoProvider(interface.Interface):
    """Provide video.
    """
    
    video_items = schema.List(title=_(u'Video Items'),
                              required=True,
                              readonly=True)

class IBasicVideoSupport(interface.Interface):
    """Provides certain information about video support.
    """

    support_enabled = schema.Bool(title=_(u'Video Support Enabled?'),
                                  required=True,
                                  readonly=True)

class IVideoSupport(IBasicVideoSupport):
    """Provides full information about video support.
    """

class IMediaActivator(interface.Interface):
    """For seeing the activation status or toggling activation."""

    media_activated = schema.Bool(title=_(u'Media Activated'),
                                  required=True,
                                  readonly=False)
