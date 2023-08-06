# coding: utf8

from django.core.exceptions import ImproperlyConfigured

from ..url import get_url


class RequestFormViewMixin(object):
    """
    Creates the form with the request object pass in during form construction.
    """

    def get_form(self, form_class):
        return form_class(self.request, **self.get_form_kwargs())


class SaveFormViewMixin(object):
    """ Saves the form after it validates. """

    def form_valid(self, form):
        self.form_save_result = form.save()
        return super(SaveFormViewMixin, self).form_valid(form)


class SuccessUrlFormViewMixin(object):
    success_url = None
    success_url_name = None

    def get_success_url(self):
        if not self.success_url and self.success_url_name:
            url = get_url(self.success_url_name)
        elif self.success_url:
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                'No URL to redirect to. Provide a success_url or '
                'success_url_name.'
            )
        return url
