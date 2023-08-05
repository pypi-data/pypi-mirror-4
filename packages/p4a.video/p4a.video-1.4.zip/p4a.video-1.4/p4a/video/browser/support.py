from zope import component
from zope import interface
from zope import schema
from p4a.video import interfaces

class IContextualVideoSupport(interfaces.IBasicVideoSupport):
    can_activate_video = schema.Bool(title=u'Can Activate Video',
                                     readonly=True)
    can_deactivate_video = schema.Bool(title=u'Can Deactivate Video',
                                       readonly=True)

class Support(object):
    """A view that returns certain information regarding p4a.video status.
    """

    interface.implements(IContextualVideoSupport)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def support_enabled(self):
        """Check to make sure an IVideoSupport utility is available and
        if so, query it to determine if support is enabled.
        """

        support = component.queryUtility(interfaces.IVideoSupport)
        if support is None:
            return False

        return support.support_enabled

    @property
    def _basic_can(self):
        if not self.support_enabled:
            return False

        if not interfaces.IAnyVideoCapable.providedBy(self.context):
            return False

        return True

    @property
    def can_activate_video(self):
        if not self._basic_can:
            return False

        mediaconfig = component.getMultiAdapter((self.context, self.request),
                                                name='video-config.html')
        return not mediaconfig.media_activated

    @property
    def can_deactivate_video(self):
        if not self._basic_can:
            return False

        mediaconfig = component.getMultiAdapter((self.context, self.request),
                                                name='video-config.html')
        return mediaconfig.media_activated
