# coding: utf8

from django.template import loader
from django.utils import six


def resolve_template(template):
    "Accepts a template object, path-to-template or list of paths"

    if isinstance(template, (list, tuple)):
        return loader.select_template(template)
    elif isinstance(template, six.string_types):
        return loader.get_template(template)
    else:
        return template
