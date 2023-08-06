# coding: utf8

from django.conf import settings
from django.views.generic import FormView, TemplateView

from coreutils.loading import load_module
from coreutils.views.form import SaveFormViewMixin, SuccessUrlFormViewMixin

RegistrationForm = load_module(getattr(
    settings,
    'AUTHENTICATION_REGISTRATION_FORM',
    'authentication.forms.RegistrationForm'
))


class RegistrationPage(SaveFormViewMixin, SuccessUrlFormViewMixin, FormView):
    form_class = RegistrationForm
    success_url_name = 'account_registration_complete'
    template_name = 'authentication/registration_form.html'

    def get_context_data(self, **kwargs):
        context = super(RegistrationPage, self).get_context_data(**kwargs)
        context['email'] = self.request.GET.get('email')
        context['beta_key'] = self.request.GET.get('key')
        return context


class RegistrationCompletePage(TemplateView):
    template_name = 'authentication/registration_complete.html'


class RegistrationClosedPage(TemplateView):
    template_name = 'authentication/registration_closed.html'
