# coding: utf8

from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from ..models import ActivationKey


class ActivatePage(TemplateView):
    errors = []
    activation_error_template_name = 'authentication/activate.html'
    activation_complete_template_name = (
        'authentication/activation_complete.html'
    )

    template_name = activation_error_template_name

    def get_context_data(self, **kwargs):
        context = super(ActivatePage, self).get_context_data(**kwargs)
        context['errors'] = self.errors
        if not self.errors:
            context['key'] = self.key
        return context

    def get(self, request, *args, **kwargs):
        try:
            self.key = ActivationKey.Activate(kwargs['activation_key'])
            self.template_name = self.activation_complete_template_name
        except ActivationKey.DoesNotExist:
            self.errors.append(_('Activation key does not exist.'))
        except ActivationKey.KeyExpired:
            self.errors.append(_('Activation key is expired.'))
        return super(ActivatePage, self).get(request, *args, **kwargs)


class ActivationCompletePage(TemplateView):
    template_name = 'authentication/activation_complete.html'
