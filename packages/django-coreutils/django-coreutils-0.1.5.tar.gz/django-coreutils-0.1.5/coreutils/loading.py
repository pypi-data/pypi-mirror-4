# coding: utf8

from django.utils.importlib import import_module as DjangoImportModule


def load_module(path):
    """
    Import a dotted module path and return the attribute/class designated by
    the last name in the path. Raise ImportError if something goes wrong.
    """
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    return getattr(DjangoImportModule(module), attr)
