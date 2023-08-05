import Acquisition
import AccessControl
import datetime

from zope import event
from zope import component
from zope import interface
from zope import schema
from zope.formlib import form
from zope import lifecycleevent

try:
    #Plone 3
    from zope.app.i18n import ZopeMessageFactory as _
except ImportError:
    from zope.i18nmessageid import MessageFactory
    _ = MessageFactory('zope')

from p4a.video import interfaces
from p4a.video.browser import media
from p4a.video.browser import widget

from p4a.fileimage.image._widget import ImageURLWidget

from p4a.common import at
from p4a.common import formatting

from Products.CMFCore import utils as cmfutils
from Products.statusmessages import interfaces as statusmessages_ifaces

from Products.Five.browser import pagetemplatefile
from Products.Five import BrowserView
try:
    #Plone 3
    from Products.Five.formlib import formbase
except ImportError:
    #Plone 4.1
    from five.formlib import formbase

def has_contentrating_support(context):
    try:
        import contentratings
    except ImportError, e:
        return False
    return True

def has_contentlicensing_support(context):
    try:
        from Products.ContentLicensing.DublinCoreExtensions.interfaces \
             import ILicensable
    except ImportError, e:
        return False

    from Products.ContentLicensing.utilities import interfaces as clifaces
    u = component.queryUtility(clifaces.IContentLicensingUtility)
    if u is None:
        return False

    return ILicensable.providedBy(context)

def has_contenttagging_support(context):
    try:
        from lovely.tag import interfaces as tagifaces
    except ImportError, e:
        return False
    return component.queryUtility(tagifaces.ITaggingEngine) is not None

class FeatureMixin(object):
    def has_contentrating_support(self):
        return has_contentrating_support(Acquisition.aq_inner(self.context))

    def has_contentlicensing_support(self):
        return has_contentlicensing_support(Acquisition.aq_inner(self.context))

    def has_contenttagging_support(self):
        return has_contenttagging_support(Acquisition.aq_inner(self.context))

class IVideoView(interface.Interface):
    def title(): pass
    def width(): pass
    def height(): pass
    def duration(): pass
    def video_type(): pass
    def has_media_player(): pass

class VideoView(object):
    """
    """

    def __init__(self, context, request):
        self.video_info = interfaces.IVideo(context)

        mime_type = unicode(context.get_content_type())
        self.media_player = component.queryAdapter(self.video_info.file,
                                                   interfaces.IMediaPlayer,
                                                   mime_type)

    def title(self): return self.video_info.title
    def width(self): return self.video_info.width
    def height(self): return self.video_info.height
    def duration(self): return self.video_info.duration
    def video_type(self): return self.video_info.video_type
    def has_media_player(self): return self.media_player is not None
    def description(self): return self.video_info.description
    def rich_description(self): return self.video_info.rich_description

class IVideoListedSingle(interface.Interface):
    def single(obj=None): pass
    def safe_video(obj=None, pos=None): pass

class VideoListedSingle(FeatureMixin):
    """Video listed single."""

    template = pagetemplatefile.ViewPageTemplateFile('video-listed-single.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.membership = cmfutils.getToolByName(context, 'portal_membership')
        self.portal_url = cmfutils.getToolByName(context, 'portal_url') \
                          .getPortalObject().absolute_url()
        self.discussion = cmfutils.getToolByName(context,
                                                 'portal_discussion')

    def __call__(self):
        return self.single()

    def _imageurlwidget(self, video):
        field = interfaces.IVideo['video_image'].bind(video)
        w = ImageURLWidget(field, self.request)
        return w()

    def portal_url(self):
        return self.portal_url

    def single(self, obj=None, pos=None, relevance=None):
        return self.template(video=self.safe_video(obj=obj,
                                                   pos=pos,
                                                   relevance=relevance))

    def safe_video(self, obj=None, pos=None, relevance=None):
        videoobj = obj
        if videoobj is None:
            videoobj = Acquisition.aq_inner(self.context)
        videoobj = interfaces.IVideo(videoobj, None)
        if videoobj is None:
            return None

        contentobj = videoobj.context
        size = 'N/A'
        if hasattr(Acquisition.aq_base(contentobj), 'getFile'):
            # a little duck typing
            filefield = contentobj.getFile()
            size = formatting.fancy_data_size(filefield.get_size())

        w = widget.MediaPlayerWidget(interfaces.IVideo['file'].bind(videoobj),
                                     self.request)()

        # IVideo.duration is a float, we need an int
        duration = int(round(videoobj.duration or 0.0))
        has_image = videoobj.video_image is not None

        author_username = author = contentobj.Creator()
        author_info = self.membership.getMemberInfo(author_username)
        if author_info is not None:
            author = author_info.get('fullname', author_username)

        creation_time = contentobj.created()
        creation_time = datetime.date(creation_time.year(),
                                      creation_time.month(),
                                      creation_time.day())
        creation_time = formatting.fancy_date_interval(creation_time)

        if self.has_contenttagging_support():
            tagview = component.getMultiAdapter(
                (contentobj, self.request),
                interface=interface.Interface,
                name=u'tag_info')
            tags = ({'name': videoobj,
                     'url': tagview.tag_url(videoobj) }
                    for videoobj in tagview.contextual_tags())
        else:
            tags = []

        avgrating = None
        rating_count = None
        if self.has_contentrating_support():
            ratingview = component.getMultiAdapter(
                (contentobj, self.request),
                interface=interface.Interface,
                name=u'user_rating_view')
            avgrating = int(ratingview.averageRating)
            rating_count = int(ratingview.numberOfRatings)

        max_length = 30
        description = ''
        count = 0
        for c in contentobj.Description():
            if c == ' ':
                count += 1
            if count >= max_length:
                break
            description += c

        if len(description) != len(contentobj.Description()):
            description += ' ...'

        commenting_count = 0
        commenting_last = None
        if self.discussion.isDiscussionAllowedFor(contentobj):
            disc = self.discussion.getDiscussionFor(contentobj)
            commenting_count = disc.replyCount(contentobj)

            for x in disc.objectValues():
                if commenting_last is None or \
                       x.created() > commenting_last.created():
                    commenting_last = x
            if commenting_last is not None:
                created = commenting_last.created()
                created = datetime.date(created.year(),
                                        created.month(),
                                        created.day())
                commenting_last = formatting.fancy_date_interval(created)
                commenting_last = commenting_last.lower()

        video = {
            'title': videoobj.title,
            'content_author': author_username,
            'content_author_name': author,
            'url': contentobj.absolute_url(),
            'size': size,
            'duration': formatting.fancy_time_amount(duration,
                                                     show_legend=False),
            'description': description,
            'icon': contentobj.getIcon(),
            'tags': tags,
            'widget': w,
            'has_image': has_image,
            'mime_type': contentobj.getContentType(),
            'imageurlwidget': self._imageurlwidget(videoobj),
            'creation_time': creation_time,
            'rating_count': rating_count,
            'avgrating': avgrating,
            'relevance': relevance,
            'commenting_count': commenting_count,
            'commenting_last': commenting_last,
            'portal_type': contentobj.portal_type,
            }

        if pos is not None:
            video['oddeven'] = ODDEVEN[pos % 2]

        return video

class VideoPageView(media.BaseMediaDisplayView, FeatureMixin, BrowserView):
    """Page for displaying video.
    """

    adapted_interface = interfaces.IVideo
    media_field = 'file'

    form_fields = form.FormFields(interfaces.IVideo)
    label = u'View Video Info'

    @property
    def template(self):
        return self.index

    def update(self):
        super(VideoPageView, self).update()
        if not interfaces.IVideo(self.context).video_type:
            self.context.plone_utils.addPortalMessage( \
                _(u'Unsupported video type'))

class PopupVideoPageView(media.BaseMediaDisplayView):
    """Page for displaying video.
    """

    adapted_interface = interfaces.IVideo
    media_field = 'file'

    form_fields = ()
    label = u'Popup Video Player'

def applyChanges(context, form_fields, data, adapters=None):
    if adapters is None:
        adapters = {}

    changed = []

    for form_field in form_fields:
        field = form_field.field
        # Adapt context, if necessary
        interface = field.interface
        adapter = adapters.get(interface)
        if adapter is None:
            if interface is None:
                adapter = context
            else:
                adapter = interface(context)
            adapters[interface] = adapter

        name = form_field.__name__
        newvalue = data.get(name, form_field) # using form_field as marker
        if (newvalue is not form_field) and (field.get(adapter) != newvalue):
            changed.append(name)
            field.set(adapter, newvalue)

    return changed

class SimpleTagging(object):

    def __init__(self, context):
        from p4a.plonetagging.content import UserTagging
        from p4a.plonetagging.utils import escape, unescape
        self.tagging = UserTagging(context)
        self.escape = escape
        self.unescape = unescape

    def _get_tags(self):
        return self.escape(self.tagging.tags)
    def _set_tags(self, v):
        if not v:
            v = []
        self.tagging.tags = self.unescape(v)
    tags = property(_get_tags, _set_tags)

class VideoEditForm(formbase.EditForm):
    """Form for editing video fields.
    """

    template = pagetemplatefile.ViewPageTemplateFile('video-edit.pt')
    form_fields = form.FormFields(interfaces.IVideo)
    form_fields = form_fields.omit('urls')
    form_fields['rich_description'].custom_widget = at.RichTextEditWidget
    label = u'Edit Video Data'
    priority_fields = ['title']

    def display_tags(self):
        username = AccessControl.getSecurityManager().getUser().getId()
        return username == self.context.getOwner().getId() and \
               has_contenttagging_support(self.context)

    def update(self):
        self.adapters = {}
        form_fields = self.form_fields
        if self.display_tags():
            from lovely.tag.interfaces import IUserTagging
            field = schema.TextLine(__name__='tags',
                                    title=u'Tags',
                                    description=u'Enter as many tags as you '
                                                u'like, separated by spaces.  '
                                                u'If you need a tag with '
                                                u'spaces, encase the tag in '
                                                u'double quotes; the double '
                                                u'quotes will be ignored.',
                                    required=False)
            field.interface = IUserTagging
            form_fields = self.form_fields + form.Fields(field)
            names = list(self.priority_fields) + ['tags']
            for field in form_fields.__FormFields_byname__.keys():
                if field not in names:
                    names.append(field)
            form_fields = form_fields.select(*names)

            simpletagging = SimpleTagging(self.context.context)
            self.adapters[IUserTagging] = simpletagging
        self.form_fields = form_fields

        super(VideoEditForm, self).update()

    def setUpWidgets(self, ignore_request=False):
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )

    @form.action(_("Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        changed = applyChanges(
            self.context, self.form_fields, data, self.adapters)
        if changed:
            attrs = lifecycleevent.Attributes(interfaces.IVideo, *changed)
            event.notify(
                lifecycleevent.ObjectModifiedEvent(self.context, attrs)
                )
            # TODO: Needs locale support. See also Five.form.EditView.
            self.status = _("Successfully updated")
        else:
            self.status = _('No changes')
        statusmessages_ifaces.IStatusMessage(
            self.request).addStatusMessage(self.status, 'info')
        redirect = self.request.response.redirect
        return redirect(self.context.absolute_url()+'/view')

class VideoEditMacros(formbase.PageForm):
    # short cut to get to macros more easily
    def __getitem__(self, name):
        if hasattr(self.template, 'macros'):
            template = self.template
        elif hasattr(self.template, 'default_template'):
            template = self.template.default_template
        else:
            raise TypeError('Could not lookup macros on the configured '
                            'template')

        if getattr(template.macros, '__get__', None):
            macros = template.macros.__get__(template)
        else:
            macros = template.macros

        if name == 'macros':
            return macros
        return macros[name]

class VideoStreamerView(object):
    """View for streaming video file as M3U.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        file_sans_ext = self.context.getId()
        pos = file_sans_ext.rfind('.')
        if pos > -1:
            file_sans_ext = file_sans_ext[:pos]

        response = self.request.response
        response.setHeader('Content-Type', 'video/x-mpegurl')
        response.setHeader('Content-Disposition',
                           'attachment; filename="%s.m3u"' % file_sans_ext)
        return self.request.URL1 + '\n'


ODDEVEN = ['even', 'odd']

class VideoContainerView(FeatureMixin):
    """View for video containers.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._video_items = None
        self._total_length = 0

        self.provider = interfaces.IVideoProvider(context)

    def video_items(self):
        return self.provider.video_items

    def has_syndication(self):
        try:
            view = self.context.restrictedTraverse('@@rss.xml')
            return True
        except:
            # it's ok if this doesn't exist, just means no syndication
            return False
