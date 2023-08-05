"""Definition of the Video content type
"""

from AccessControl import ClassSecurityInfo
from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions as cmf_permissions
from Products.validation import V_REQUIRED

from xhostplus.videojs import videojsMessageFactory as _
from xhostplus.videojs.interfaces import IVideo
from xhostplus.videojs.config import PROJECTNAME

security = ClassSecurityInfo()

VideoSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.FileField('webm_video.webm',
                required = False,
                languageIndependent = False,
                allowable_content_types=('video/webm',),
                default_content_type='video/webm',
                validators = (
                    ('isNonEmptyFile', V_REQUIRED),
                ),
                widget = atapi.FileWidget(
                     description = _(u"The video in the WebM format"),
                     label= _(u"WebM File"),
                     show_content_type = False,
                ),
                storage=atapi.AttributeStorage(),
    ),

    atapi.FileField('h264_video.mp4',
                required = False,
                languageIndependent = False,
                allowable_content_types=('video/mp4',),
                default_content_type='video/mp4',
                validators = (
                    ('isNonEmptyFile', V_REQUIRED),
                ),
                widget = atapi.FileWidget(
                     description = _(u"The video in the H.264 format"),
                     label= _(u"H.264 File"),
                     show_content_type = False,
                ),
                storage=atapi.AttributeStorage(),
    ),

    atapi.FileField('ogg_video.ogg',
                required = False,
                languageIndependent = False,
                allowable_content_types=('video/ogg',),
                default_content_type='video/ogg',
                validators = (
                    ('isNonEmptyFile', V_REQUIRED),
                ),
                widget = atapi.FileWidget(
                     description = _(u"The video in the OGG/Theora format"),
                     label= _(u"OGG File"),
                     show_content_type = False,
                ),
                storage=atapi.AttributeStorage(),
    ),

    atapi.FileField('flv_video.flv',
                required = False,
                languageIndependent = False,
                allowable_content_types=('video/x-flv',),
                default_content_type='video/x-flv',
                validators = (
                    ('isNonEmptyFile', V_REQUIRED),
                ),
                widget = atapi.FileWidget(
                     description = _(u"The video in the FLV format"),
                     label= _(u"FLV File"),
                     show_content_type = False,
                ),
                storage=atapi.AttributeStorage(),
    ),

    atapi.StringField('webm_url',
        required = False,
        searchable = False,
        languageIndependent = False,
        # either absolute url or relative url
        validators = (),
        widget = atapi.StringWidget(
            description=_(u"A URL to the video in the WebM format"),
            label=_(u"WebM URL"),
        )
    ),

    atapi.StringField('h264_url',
        required = False,
        searchable = False,
        languageIndependent = False,
        # either absolute url or relative url
        validators = (),
        widget = atapi.StringWidget(
            description=_(u"A URL to the video in the H.264 format"),
            label=_(u"H.264 URL"),
        )
    ),

    atapi.StringField('ogg_url',
        required = False,
        searchable = False,
        languageIndependent = False,
        # either absolute url or relative url
        validators = (),
        widget = atapi.StringWidget(
            description=_(u"A URL to the video in the OGG format"),
            label=_(u"OGG URL"),
        )
    ),

    atapi.StringField('flv_url',
        required = False,
        searchable = False,
        languageIndependent = False,
        # either absolute url or relative url
        validators = (),
        widget = atapi.StringWidget(
            description=_(u"A URL to the video in the FLV format"),
            label=_(u"FLV URL"),
        )
    ),

    atapi.StringField('youtube_url',
        required = False,
        searchable = False,
        languageIndependent = False,
        validators = (),
        widget = atapi.StringWidget(
            description=_(u"A URL to the video on Youtube"),
            label=_(u"Youtube URL"),
        )
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

VideoSchema['title'].storage = atapi.AnnotationStorage()
VideoSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(VideoSchema, moveDiscussion=False)

class Video(base.ATCTContent):
    """A video type"""
    implements(IVideo)

    meta_type = "Video"
    schema = VideoSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def getWebm_file(self):
        getter = getattr(self, 'getWebm_video.webm')
        f = getter()
        if f and f.get_size():
            return f
        return None

    def getH264_file(self):
        getter = getattr(self, 'getH264_video.mp4')
        f = getter()
        if f and f.get_size():
            return f
        return None

    def getOgg_file(self):
        getter = getattr(self, 'getOgg_video.ogg')
        f = getter()
        if f and f.get_size():
            return f
        return None

    def getFlv_file(self):
        getter = getattr(self, 'getFlv_video.flv')
        f = getter()
        if f and f.get_size():
            return f
        return None

    def setWebm_file(self, value):
        setter = getattr(self, 'setWebm_video.webm')
        setter(value)

    def setH264_file(self, value):
        setter = getattr(self, 'setH264_video.mp4')
        setter(value)

    def setOgg_file(self, value):
        setter = getattr(self, 'setOgg_video.ogg')
        setter(value)

    def setFlv_file(self, value):
        setter = getattr(self, 'setFlv_video.flv')
        setter(value)

    security.declarePublic('getYoutubeEmbed')
    def getYoutubeEmbed(self):
        vid = ""
        src = self.getYoutube_url()

        if not src:
            return ""

        if "/embed/" in src:
            vid = src.split("/embed/")[1].strip(" /")

        if "watch?v=" in src:
            vid = src.split("watch?v=")[1].split("&")[0].strip(" /")

        if not vid:
            return ""

        return """<iframe width="560" height="315" frameborder="0" allowfullscreen="allowfullscreen"
                          src="http://www.youtube.com/embed/%s" ></iframe>""" % vid

    security.declarePublic('getWebMAbsoluteURL')
    def getWebMAbsoluteURL(self):
        if self.getWebm_url():
            return self.getWebm_url()
        if self.getWebm_file():
            setattr(self.getWebm_file(), 'content_type', 'video/webm')
            return "%s/webm_video.webm" % self.absolute_url()
        return None

    security.declarePublic('getH264AbsoluteURL')
    def getH264AbsoluteURL(self):
        if self.getH264_url():
            return self.getH264_url()
        if self.getH264_file():
            setattr(self.getH264_file(), 'content_type', 'video/mp4')
            return "%s/h264_video.mp4" % self.absolute_url()
        return None

    security.declarePublic('getOGGAbsoluteURL')
    def getOGGAbsoluteURL(self):
        if self.getOgg_url():
            return self.getOgg_url()
        if self.getOgg_file():
            setattr(self.getOgg_file(), 'content_type', 'video/ogg')
            return "%s/ogg_video.ogg" % self.absolute_url()
        return None

    security.declarePublic('getFLVAbsoluteURL')
    def getFLVAbsoluteURL(self):
        if self.getFlv_url():
            return self.getFlv_url()
        if self.getFlv_file():
            setattr(self.getFlv_file(), 'content_type', 'video/x-flv')
            return "%s/flv_video.flv" % self.absolute_url()
        return None

    security.declarePublic('getFlowplayerVideoURL')
    def getFlowplayerVideoURL(self):
        h264 = self.getH264AbsoluteURL()
        flv = self.getFLVAbsoluteURL()
        webm = self.getWebMAbsoluteURL()

        if flv:
            return flv
        if h264:
            return h264
        return webm

    security.declareProtected(cmf_permissions.ModifyPortalContent, 'post_validate')
    def post_validate(self, REQUEST=None, errors=None):
        def any_set(iterable):
            for i in iterable:
                if i: return True
            return False

        def all_set(iterable):
            for i in iterable:
                if not i: return False
            return True

        webm_file = REQUEST.get('webm_video.webm_file', None)
        h264_file = REQUEST.get('h264_video.mp4_file', None)
        ogg_file = REQUEST.get('ogg_video.ogg_file', None)
        flv_file = REQUEST.get('flv_video.flv_file', None)

        if not webm_file and not REQUEST.get('webm_video.webm_delete', None) == 'delete':
            webm_file = self.getWebm_file()

        if not h264_file and not REQUEST.get('h264_video.mp4_delete', None) == 'delete':
            h264_file = self.getH264_file()

        if not ogg_file and not REQUEST.get('ogg_video.ogg_delete', None) == 'delete':
            ogg_file = self.getOgg_file()

        if not flv_file and not REQUEST.get('flv_video.flv_delete', None) == 'delete':
            flv_file = self.getFlv_file()

        webm_url = REQUEST.get('webm_url', None)
        h264_url = REQUEST.get('h264_url', None)
        ogg_url = REQUEST.get('ogg_url', None)
        flv_url = REQUEST.get('flv_url', None)

        youtube_url = REQUEST.get('youtube_url', None)

        if youtube_url and any_set((webm_file, h264_file, ogg_file, flv_file, webm_url, h264_url, ogg_url, flv_url)):
            error_message = _(u"You cannot set a Youtube URL combined with any other video source")
            errors['youtube_url'] = error_message
        elif not youtube_url:
            if not any_set((webm_file, h264_file, ogg_file, flv_file, webm_url, h264_url, ogg_url, flv_url)):
                error_message = _(u"Any of the fields must be set")
                errors['webm_video.webm'] = error_message
                errors['h264_video.mp4'] = error_message
                errors['ogg_video.ogg'] = error_message
                errors['flv_video.flv'] = error_message
                errors['webm_url'] = error_message
                errors['h264_url'] = error_message
                errors['ogg_url'] = error_message
                errors['flv_url'] = error_message

            if all_set((webm_file, webm_url)):
                error_message = _(u"You cannot set file and URL")
                errors['webm_video.webm'] = error_message
                errors['webm_url'] = error_message

            if all_set((h264_file, h264_url)):
                error_message = _(u"You cannot set file and URL")
                errors['h264_video.mp4'] = error_message
                errors['h264_url'] = error_message

            if all_set((ogg_file, ogg_url)):
                error_message = _(u"You cannot set file and URL")
                errors['ogg_video.ogg'] = error_message
                errors['ogg_url'] = error_message

            if all_set((flv_file, flv_url)):
                error_message = _(u"You cannot set file and URL")
                errors['flv_video.flv'] = error_message
                errors['flv_url'] = error_message

atapi.registerType(Video, PROJECTNAME)
