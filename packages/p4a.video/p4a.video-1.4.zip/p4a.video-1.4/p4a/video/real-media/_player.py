from zope import interface
from zope import component
from p4a.video import interfaces
from Products.CMFCore import utils as cmfutils

class RealVideoPlayer(object):
    interface.implements(interfaces.IMediaPlayer)
    component.adapts(object)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self, downloadurl, imageurl, width, height):

        if not (width and height):
            width = 320
            height = 240

        url = "%s?embed" % downloadurl

        return """
            <OBJECT ID="videoObj" WIDTH="%(width)s" HEIGHT="%(width)s" CLASSID="clsid:CFCDAA03-8BE4-11cf-B84B-0020AFBBCCFA">
              <PARAM NAME="controls" VALUE="ImageWindow" />
              <PARAM NAME="console" VALUE="Clip1" />
              <PARAM NAME="autostart" VALUE="false"/>
              <PARAM NAME="src" VALUE="%(url)s"/>
                <EMBED WIDTH="%(width)s" HEIGHT="%(height)s" AUTOSTART="false" CONTROLS="ImageWindow" CONSOLE="Clip1" TYPE="audio/x-pn-realaudio-plugin"
                   SRC="%(url)s"/>
            </OBJECT>
            <OBJECT ID="controlObj" WIDTH="%(width)s" HEIGHT="55" CLASSID="clsid:CFCDAA03-8BE4-11cf-B84B-0020AFBBCCFA">
              <PARAM VALUE="All" NAME="controls"/>
              <PARAM VALUE="Clip1" NAME="console"/>
                <EMBED WIDTH="%(width)s" HEIGHT="55" AUTOSTART="false" CONTROLS="All" CONSOLE="Clip1" TYPE="audio/x-pn-realaudio-plugin"/>
            </OBJECT>
            """ % {'url': downloadurl,
                   'height': height, 
                   'width': width}

        


