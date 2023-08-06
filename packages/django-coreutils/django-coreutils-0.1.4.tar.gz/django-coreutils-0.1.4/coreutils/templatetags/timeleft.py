# coding: utf8

from django import template
from django.utils.timesince import timesince
from django.utils import timezone

register = template.Library()


def get_timeleft(value):
    return timesince(timezone.now(), value)

register.filter('timeleft', get_timeleft)
