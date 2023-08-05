from zope import interface
from p4a.video import interfaces
from p4a.subtyper.interfaces import (IPortalTypedDescriptor,
                                     IPortalTypedFolderishDescriptor)

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('p4a.video')

class VideoDescriptor(object):
    interface.implements(IPortalTypedDescriptor)

    title = _(u'Video')
    description = _(u'Video-based media content')
    type_interface = interfaces.IVideoEnhanced
    for_portal_type = 'File'

class AbstractVideoContainerDescriptor(object):
    interface.implements(IPortalTypedFolderishDescriptor)

    title = _(u'Video Container')
    description = _(u'Container for holding Video-based media content')
    type_interface = interfaces.IVideoContainerEnhanced

class FolderVideoContainerDescriptor(AbstractVideoContainerDescriptor):
    for_portal_type = 'Folder'

class TopicVideoContainerDescriptor(AbstractVideoContainerDescriptor):
    for_portal_type = 'Topic'
