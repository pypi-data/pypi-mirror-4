# coding: utf8


from django.core.mail import send_mail
from django.template.context import Context

from .template import resolve_template


def send_email(subject, message, sender, recipients):
    """
    Sends and email with the given subject and message to the given recipients.
    """
    return send_mail(
        subject, message, sender, recipients, fail_silently=False
    )


def send_templated_email(template, subject, recipients, sender, context={}):
    """
    Sends and email using the given template to the given recipients.
    """
    return send_email(
        subject,
        resolve_template(template).render(Context(context)),
        sender,
        recipients,
    )
