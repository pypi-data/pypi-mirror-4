# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.contrib.sites.models import Site

def fancy_url_validator(value):
    """
    Make sure 'value' is either a valid URL, or valid absolute URL.
    @raise: ValidationError
    """
    validate = URLValidator()
    try:
        validate(value)
    except ValidationError:
        validate('http://%s%s' % (Site.objects.get_current().domain, value))