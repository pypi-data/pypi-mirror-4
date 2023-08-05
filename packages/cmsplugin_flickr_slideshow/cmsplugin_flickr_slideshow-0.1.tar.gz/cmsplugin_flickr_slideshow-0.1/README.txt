cmsplugin_flickr_slideshow
==========================

Plugin for Django CMS that makes easy to embed Flickr slideshows.

Download: https://github.com/Immediatic/cmsplugin_flickr_slideshow

Requirements:
- django-cms-2.3 or greater
- django: 1.4 or greater

Last tested with:
- django-cms-2.3.1
- django: 1.4.1

Setup
-----

- make sure requirements are installed and properly working
- add cmsplugin_flickr_slideshow to python path
- add 'cmsplugin_flickr_slideshow' to INSTALLED_APPS
- run 'python manage.py migrate cmsplugin_flickr_slideshow' if using South or 'python manage.py syncdb' if not using South

Settings
--------

- CMS_FLICKR_SLIDESHOW_DEFAULT_ALLOW_FULLSCREEN    (Default True)
- CMS_FLICKR_SLIDESHOW_DEFAULT_WIDTH               (Default 400)
- CMS_FLICKR_SLIDESHOW_DEFAULT_HEIGHT              (Default 300)

Credits
-------

This plugin derives from [cmsplugin-youtube](https://bitbucket.org/xenofox/cmsplugin-youtube) and has been customized for Vimeo movies.

The plugin is available on [Django Packages](http://www.djangopackages.com/packages/p/cmsplugin_flickr_slideshow/).
