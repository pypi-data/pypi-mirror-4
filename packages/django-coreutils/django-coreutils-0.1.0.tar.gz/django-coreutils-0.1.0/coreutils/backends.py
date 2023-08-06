# coding: utf8

from .loading import load_module
from .settings import get_setting


def get_backend(settings_name, default, instantiate=True):
    """
    Returns the backend declared by settings_name, or default if
    settings_name is not found. If the instantiate flag is set
    (the default is set) then the backend will be instantiated before
    being returned.
    """
    backend = load_module(get_setting(settings_name, default=default))

    if backend and instantiate:
        backend = backend()

    return backend
