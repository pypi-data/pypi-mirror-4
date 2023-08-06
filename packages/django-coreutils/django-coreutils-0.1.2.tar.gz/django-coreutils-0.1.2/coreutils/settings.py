# coding: utf8

from django.conf import settings


def get_setting(*args, **kwargs):
    """
    Returns the settings value for the given options. If not found the last
    argument provided or None will be returned.
    """
    arg_count = len(args)

    default = None
    if 'default' in kwargs:
        default = kwargs.pop('default')

    for i in range(arg_count):
        if hasattr(settings, args[i]):
            return getattr(settings, args[i])

    return default
