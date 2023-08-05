from django.db import models
from django.utils.translation import ugettext as _

from cms.models import CMSPlugin

from cmsplugin_flickr_slideshow import settings

class FlickrSlideshow(CMSPlugin):
    flikr_id = models.CharField(_('video id'), max_length=60)
    flashvars = models.CharField(_('flashvars'), max_length=1000)

    allowfullscreen = models.BooleanField(
        _('allow full screen'),
        default=settings.CMS_FLICKR_SLIDESHOW_DEFAULT_ALLOW_FULLSCREEN
    )

    width = models.IntegerField(_('width'),
            default=settings.CMS_FLICKR_SLIDESHOW_DEFAULT_WIDTH)
    height = models.IntegerField(_('height'),
            default=settings.CMS_FLICKR_SLIDESHOW_DEFAULT_HEIGHT)

    def __unicode__(self):
        return u'%s' % (self.flikr_id,)
