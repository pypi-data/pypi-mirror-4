# coding: utf8

from django import template

register = template.Library()


def get_range(value):
    return range(value)

register.filter('range', get_range)
