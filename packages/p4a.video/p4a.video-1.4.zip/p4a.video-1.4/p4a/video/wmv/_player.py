from zope import interface
from zope import component
from p4a.video import interfaces

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('p4a.video')

class WMVVideoPlayer(object):
    interface.implements(interfaces.IMediaPlayer)
    component.adapts(object)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self, downloadurl, imageurl, width, height):
        if not (width and height):
            width = 320
            height = 240

        argstring = 'width=%(width)s, height=%(height)s' % {'width': width, 'height': height}
        argstring = 'showclose=false, ' + argstring
        
        if imageurl:
            result = """
                <div class="hVlog">
                  <a href="%(url)s" class="hVlogTarget" type="video/x-ms-wmv" onclick="vPIPPlay(this, '%(args)s', '', ''); return false;">
                      <img src="%(imageurl)s" />
                      </a>
                <br />""" % {'url': downloadurl, 
                             'imageurl': imageurl or '',
                             'args': argstring}
        else:
            result = ""

        result += """          
                  <a href="%(url)s" type="video/x-ms-wmv" onclick="vPIPPlay(this, '%(args)s', '', ''); return false;">
                  %(msg)s</a>
                  </div>        
                 """ % {'url': downloadurl, 
                        'args': argstring,
                        'msg':_(u'Play WindowsMedia version')}
        return result
        
