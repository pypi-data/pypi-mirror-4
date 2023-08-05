from zope import component
from zope.app.form.browser import widget
from p4a.video import interfaces
from p4a.fileimage import file
from p4a.fileimage.image._widget import ImageURLWidget

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('p4a.video')

class MediaPlayerWidget(file.FileDownloadWidget):
    """Widget which produces some form of media player.
    """

    def __call__(self):
        file_present = True
        if not self._data:
            file_present = False

        url = self.url
        if not url:
            file_present = False

        if not file_present:
            return widget.renderElement(u'span',
                                        cssClass='media-absent media-player',
                                        contents=_('No media to play'))


        video = self.context.context
        if video.video_image is not None:
            field = interfaces.IVideo['video_image'].bind(video)
            imageurl = ImageURLWidget(field, self.request).url or None
        else:
            imageurl = None

        field = self.context
        contentobj = field.context.context

        width = video.width
        height = video.height
        mime_type = unicode(contentobj.get_content_type())
        media_player = component.queryAdapter(field,
                                              interface=interfaces.IMediaPlayer,
                                              name=mime_type)

        absolute_url = video.context.absolute_url()        


        if media_player is None:
            return widget.renderElement \
                   (u'span',
                    cssClass='player-not-available media-player',
                    contents=_("No available player for mime type '%s'"
                               % mime_type))
               
        s = u'<div class="media-player">%s</div>' % media_player(absolute_url, imageurl, width, height)
        return s
