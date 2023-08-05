from zope import interface
from zope import component
from p4a.video import interfaces

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('p4a.video')


class SWFVideoPlayer(object):
    interface.implements(interfaces.IMediaPlayer)
    component.adapts(object)

    def __init__(self, context):
        self.context = context

    def __call__(self, downloadurl, imageurl, width, height):

        if not (width and height):
            width = 320
            height = 240
        height +=22

        contentobj = self.context.context.context
        file_url = contentobj.absolute_url()+'/download'

        videoobj = interfaces.IVideo(contentobj)

        if not videoobj.width or not videoobj.height:
            msg= _(u'No dimensions specified for flash video')
            return '''<div class="flas-movie no-dimensions">
            %s
            </div>''' % msg


        title = contentobj.Title()
        if isinstance(title, str):
            title = title.decode('utf8')

        s = u'''
            <div class="flash-movie">
              <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
                      codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" 
                      width="%(width)s" height="%(height)s" id="Untitled-1" align="middle">
                <param name="allowScriptAccess" value="sameDomain" />
                <param name="movie" value="%(file_url)s" />
                <param name="quality" value="high" />
                <param name="bgcolor" value="#ffffff" />
                <embed src="%(file_url)s" quality="high" bgcolor="#ffffff"
                       width="%(width)s" height="%(height)s" name="%(title)s"
                       align="middle" allowScriptAccess="sameDomain"
                       type="application/x-shockwave-flash"
                       pluginspage="http://www.adobe.com/go/getflashplayer" />
              </object>
            </div>
        ''' % {'file_url': file_url,
               'width': width,
               'height': height,
               'title': title}
        return s
