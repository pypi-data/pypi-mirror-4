# coding: utf8


from django.conf import settings
from django.core.mail import send_mail
from django.template.context import Context
from django.utils.translation import ugettext as _

from .template import resolve_template


def send_email(subject, message, recipients):
    """
    Sends and email with the given subject and message to the given recipients.
    """
    return send_mail(
        subject, message,
        settings.SUPPORT_EMAIL,
        recipients,
        fail_silently=False
    )


def send_templated_email(template, subject, recipients, context={}):
    """
    Sends and email using the given template to the given recipients.
    """
    return send_email(
        subject,
        resolve_template(template).render(Context(context)),
        recipients,
    )


def send_beta_key_email(key):
    """ Sends the user their beta key via email. """
    return send_templated_email(
        'emails/beta_key.txt',
        _('Here is your beta key!'),
        (key.email,),
        context={
            'key': key
        },
    )
