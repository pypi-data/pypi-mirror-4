from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from cmsplugin_flickr_slideshow.models import FlickrSlideshow as FlickrSlideshowModel

from django.utils.translation import ugettext as _

class FlickrSlideshowPlugin(CMSPluginBase):
    model = FlickrSlideshowModel
    name = _("Flickr Slideshow")
    render_template = "cmsplugin_flickr_slideshow/embed.html"

    def render(self, context, instance, placeholder):
        context.update({
            'object': instance,
            'placeholder': placeholder
        })
        return context

plugin_pool.register_plugin(FlickrSlideshowPlugin)
