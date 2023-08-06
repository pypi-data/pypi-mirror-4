# coding: utf8


class SaveFormViewMixin(object):
    """ Saves the form after it validates. """

    def form_valid(self, form):
        self.form_save_result = form.save()
        return super(SaveFormViewMixin, self).form_valid(form)


class RequestFormViewMixin(object):
    """
    Creates the form with the request object pass in during form construction.
    """

    def get_form(self, form_class):
        return form_class(self.request, **self.get_form_kwargs())
