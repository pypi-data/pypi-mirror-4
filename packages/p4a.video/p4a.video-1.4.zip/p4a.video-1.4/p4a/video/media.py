from zope import interface
from zope import component
from p4a import subtyper
from p4a.video import interfaces

class MediaActivator(object):
    """An adapter for seeing the activation status or toggling activation.
    """

    interface.implements(interfaces.IMediaActivator)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = context

    media_activated = subtyper.activated('p4a.video.Video', 'context')
