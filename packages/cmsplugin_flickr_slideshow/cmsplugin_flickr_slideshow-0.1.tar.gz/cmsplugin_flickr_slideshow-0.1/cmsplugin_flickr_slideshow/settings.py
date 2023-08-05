"""
Convenience module for access of custom youtube application settings,
which enforces default settings when the main settings module does not
contain the appropriate settings.
"""
from django.conf import settings

# Allow full screen
CMS_FLICKR_SLIDESHOW_DEFAULT_ALLOW_FULLSCREEN = getattr(settings, 'CMS_FLICKR_SLIDESHOW_DEFAULT_ALLOW_FULLSCREEN', True)

# Width & Height
CMS_FLICKR_SLIDESHOW_DEFAULT_WIDTH = getattr(settings, 'CMS_FLICKR_SLIDESHOW_DEFAULT_WIDTH', 400)
CMS_FLICKR_SLIDESHOW_DEFAULT_HEIGHT = getattr(settings, 'CMS_FLICKR_SLIDESHOW_DEFAULT_HEIGHT', 300)
