# coding: utf8

import os

from django.conf import settings
from django.db import models
from django.db.models.loading import get_model
from django.template import Context
from django.utils import timezone

from .template import resolve_template

COUNT = int(getattr(settings, 'COREUTILS_KEYED_MODEL_KEY_LENGTH', 32))

POSSIBLE_KEY_VALUES = getattr(
    settings,
    'COREUTILS_KEYED_MODEL_KEY_VALUES',
    '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
)


class InvalidIdentifier(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return str(self.data)

    def __unicode__(self):
        return self.data


def get_identifier(model):
    """
    Gets the model identifier string for a model instance by concatenating the
    app_label and the class name of the model, separated by periods, as well as
    the primary key, separated by a colon:

        '<app_label>.<class name>:<primary key>'

    For example:

        'auth.User:1'

    will be returned for an instance of django's contrib -> auth -> user model
    instance with a pk of 1.
    """
    if isinstance(model, str) or isinstance(model, unicode):
        return 'str.str:%s' % model
    return '%s.%s:%d' % (
        model._meta.app_label,
        model.__class__.__name__,
        model.pk
    )


def is_valid_identifier(identifier):
    """ Returns True if the identifier is valid, or False otherwise. """
    # it's easy if they didn't give us anything!
    if not identifier or not (identifier.count(':') or identifier.count('.')):
        return False

    data = identifier.split(':')
    if not len(data) == 2:
        return False

    model_path, pk = data

    data = model_path.split('.')
    if not len(data) == 2:
        return False

    module, model = data

    if module and model and pk:
        return True

    return False


def get_model_identifier(model):
    """
    Gets the model identifier string for a model by concatenating the
    app_label and the class name of the model, separated by periods:

        '<app_label>.<class name>'

    For example:

        'auth.User'

    will be returned for an instance of django's contrib/auth/user model.
    """
    return '%s.%s' % (
        model._meta.app_label,
        model.__class__.__name__,
    )


def get_model_class(identifier):
    """
    Gets the model class for a given identifier string. The identifier string
    must be in the format of:

        '<app_label>.<class name>'

    For example:

        'auth.User'

    will return django's contrib -> auth -> user model class.
    """
    return get_model(*identifier.split('.'))


def translate_identifier(identifier, run_query=False):
    """
    Gets the model class and primary key for a given identifier string. The
    identifier string must be in the format of:

        '<app_label>.<class name>:<primary key>'

    For example:

        'auth.User:1'

    will return an instance of django's contrib -> auth -> user model class
    with the primary key value of 1. If the run_query flag is set the model
    instance will be returned instead of the pk.
    """
    if not is_valid_identifier(identifier):
        return None, None

    identifier, value = identifier.split(':')

    if identifier.count('str'):
        return value.__class__, value

    model = get_model_class(identifier)
    value = int(value)

    if run_query:
        return model, model.objects.get(pk=value)

    return model, value


def translate_and_get(identifier):
    """
    Gets the model instance for a given identifier string. The identifier
    string must be in the format of:

        '<app_label>.<class name>:<primary key>'

    For example:

        'auth.User:1'

    will return an instance of django's contrib -> auth -> user model class
    with the primary key value of 1.
    """
    return translate_identifier(identifier, True)[1]


class ConsumableModel(models.Model):
    consumed = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def consume(self, commit=True):
        self.consumed = True

        if commit:
            self.save()


class ContextableModel(object):
    disallowed_fields = []
    __disallowed_fields = ['_state']

    def get_context_data(self):
        context = self.__dict__

        for field in self.disallowed_fields:
            if field in context:
                del context[field]

        return context


class DeletableModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def mark_deleted(self, commit=True):
        """
        Marks the object deleted and updates the deleted_on timestamp. If the
        commit flag is set the object will be saved afterwards.
        """

        self.is_deleted = True
        self.deleted_on = timezone.now()

        if commit:
            self.save()

    def unmark_deleted(self, commit=True):
        """
        Un-marks the object deleted and updates the deleted_on timestamp. If
        the commit flag is set the object will be saved afterwards.
        """

        self.is_deleted = False
        self.deleted_on = None

        if commit:
            self.save()


class ExpiringModel(models.Model):
    expires = models.DateTimeField()

    class Meta:
        abstract = True

    def get_is_expired(self):
        return self.expires <= timezone.now()
    is_expired = property(get_is_expired)

    def expire(self, commit=True):
        self.expires = timezone.now()

        if commit:
            self.save()


class KeyedModel(models.Model):
    key = models.CharField(max_length=COUNT, blank=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(KeyedModel, self).__init__(*args, **kwargs)
        if not self.key:
            self.generage_key(commit=False)

    def __unicode__(self):
        return self.key

    @staticmethod
    def GenerateKey():
        return ''.join(map(
            lambda x: POSSIBLE_KEY_VALUES[
                ord(x) % len(POSSIBLE_KEY_VALUES)
            ], os.urandom(COUNT)
        ))

    def generage_key(self, commit=True):
        self.key = self.GenerateKey()

        if commit:
            self.save()

    def save(self, **kwargs):
        if not self.key:
            self.generage_key(commit=False)
        return super(KeyedModel, self).save(**kwargs)


class PublishableModel(models.Model):
    is_published = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def publish(self, commit=True):
        self.is_published = True

        if commit:
            self.save()

    def unpublish(self, commit=True):
        self.is_published = False

        if commit:
            self.save()


class ReferencingModel(models.Model):
    reference_id = models.IntegerField(default=-1)
    reference_type = models.CharField(max_length=50, default='')

    class Meta:
        abstract = True

    def get_referenced_model(self):
        return get_model_class(self.reference_type)
    referenced_model = property(get_referenced_model)

    def get_referenced_item(self):
        if self.reference_id and self.reference_id > 0:
            return self.referenced_model.objects.get(pk=self.reference_id)
    referenced_item = property(get_referenced_item)


class RenderableModel(object):
    def render(self, template, extra_context={}):
        context = self.get_context_data()
        context.update(extra_context)

        return resolve_template(template).render(Context(context))
