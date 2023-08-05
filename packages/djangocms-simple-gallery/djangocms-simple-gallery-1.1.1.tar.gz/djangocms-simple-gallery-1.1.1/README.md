# djangocms-simple-gallery

Simple gallery plugin for django-cms. Still in development.

## Installation
You can easily install it via pip:

* `pip install djangocms-simple-gallery`
* add `djangocms_simple_gallery` to your `INSTALLED_APPS`
* run `syncdb` and `migrate`

## Requirements
* django-filer
* easy-thumbnails

## Settings
### DANGOCMS_SIMPLE_GALLERY_TEMPLATES
A Tuple of Tuples containing the available Templates:

`(('djangocms_gallery/default.html', _('default'),)`

### DANGOCMS_SIMPLE_GALLERY_ADVANCED_OPTIONS
Default is False. If True, additional options will be available in the admin.