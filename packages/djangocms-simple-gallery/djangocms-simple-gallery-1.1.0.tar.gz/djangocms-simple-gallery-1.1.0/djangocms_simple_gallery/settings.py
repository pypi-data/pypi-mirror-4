# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


DEFAULT_GALLERY_TEMPLATES = (
    ('djangocms_simple_gallery/default.html', _('default')),
)

DEFAULT_ADVANCED_OPTIONS = True


GALLERY_TEMPLATES = getattr(settings, 'DJANGOCMS_SIMPLE_GALLERY_TEMPLATES', DEFAULT_GALLERY_TEMPLATES)
ADVANCED_OPTIONS = getattr(settings, 'DJANGOCMS_SIMPLE_GALLERY_ADVANCED_OPTIONS', DEFAULT_ADVANCED_OPTIONS)