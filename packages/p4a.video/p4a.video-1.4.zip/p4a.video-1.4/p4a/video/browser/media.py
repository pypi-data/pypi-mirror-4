from zope import interface
from zope.annotation import interfaces as annointerfaces
from zope.formlib import form

from p4a.video import interfaces
from p4a.video import media
from p4a.video.browser import widget
from p4a.common import feature

_marker = object()

class ToggleEnhancementsView(object):
    """
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        was_activated = self.media_activated
        self.media_activated = not was_activated
        response = self.request.response

        if was_activated:
            activated = 'Media+deactivated'
        else:
            activated = 'Media+activated'

        response.redirect(self.context.absolute_url() + \
                          '/view?portal_status_message='+activated)

    def _set_media_activated(self, v):
        interfaces.IMediaActivator(self.context).media_activated = v
    def _get_media_activated(self):
        return interfaces.IMediaActivator(self.context).media_activated
    media_activated = property(_get_media_activated, _set_media_activated)

class BaseMediaDisplayView(form.PageDisplayForm):
    """Base view for displaying media.
    """

    adapted_interface = None
    media_field = None

    def _media_player(self):
        video = self.adapters.get(self.adapted_interface,
                                  self.adapted_interface(self.context))
        field = self.adapted_interface[self.media_field].bind(video)
        player_widget = widget.MediaPlayerWidget(field, self.request)
        player_widget.name = self.prefix + 'media_player'
        player_widget._data = field.get(video)
        return player_widget

    def update(self):
        super(BaseMediaDisplayView, self).update()
        player_widget = self._media_player()
        self.widgets += form.Widgets([(None, player_widget)], len(self.prefix))
