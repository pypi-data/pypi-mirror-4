# coding: utf8

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from .utils.email import send_templated_email


class ContactForm(forms.Form):
    name = forms.CharField(
        error_messages={'required': _('Your Name is Required.')},
        required=True,
    )

    email = forms.EmailField(
        error_messages={
            'invalid': _('Please Enter a Valid Email.'),
            'required': _('Your Email is Required.')
        }, required=True,
    )

    message = forms.CharField(
        error_messages={'required': _('Your Message is Required.')},
        required=True,
        widget=forms.Textarea,
    )

    def clean_message(self):
        message = self.cleaned_data['message']

        if not message:
            raise forms.ValidationError(_('Your Message is Required.'))

        return message

    def clean_name(self):
        name = self.cleaned_data['name']

        if not name:
            raise forms.ValidationError(_('Your Name is Required.'))

        return name

    def send_email(self):
        if self.is_valid():
            body = self.cleaned_data['message']
            from_email = settings.SUPPORT_EMAIL
            recipients = [a[1] for a in settings.CONTACT_NOTIFY]

            subject = 'Message From: %s (%s)' % (
                self.cleaned_data['name'],
                self.cleaned_data['email']
            )

            return send_templated_email(
                template='contact',
                subject=subject,
                recipients=recipients,
                context={
                    'body': body,
                    'from': from_email,
                    'recipients': recipients,
                    'subject': subject,
                },
            )

    def save(self):
        self.send_email()


class RequestFormMixin(object):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        return super(RequestFormMixin, self).__init__(*args, **kwargs)
