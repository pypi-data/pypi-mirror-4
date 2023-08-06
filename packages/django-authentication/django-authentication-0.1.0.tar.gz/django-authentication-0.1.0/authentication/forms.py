# coding: utf8

from datetime import timedelta
import logging

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from .models import ActivationKey
from .utils import get_user_model

log = logging.getLogger('authentication.forms.registration')


class ActivationForm(forms.Form):
    activation_key = forms.CharField(required=True)

    def clean_activation_key(self):
        activation_key = self.cleaned_data['activation_key']
        try:
            return ActivationKey.objects.get(
                key=activation_key, expires__gte=now()
            )
        except ActivationKey.DoesNotExist:
            raise forms.ValidationError(
                _('That activation key does not exist.')
            )

    def save(self):
        key = self.cleaned_data['activation_key']
        key.activate()


class AuthenticationForm(AuthenticationForm):
    """
    Override the default AuthenticationForm to force behavior.
    """
    email = forms.EmailField(
        label=_("Email"), max_length=75, required=True, error_messages={
            'invalid': _('Please enter a valid email.'),
            'required': _('Your email is required.')
        }
    )

    message_incorrect_password = _(
        'Please enter a correct email and password.'
    )
    message_inactive = _('Your account is inactive.')

    def __init__(self, request=None, *args, **kwargs):
        super(AuthenticationForm, self).__init__(request, *args, **kwargs)
        del self.fields['username']
        self.fields.keyOrder = ['email', 'password']

        self.fields['password'].error_messages = {
            'invalid': _('Please enter a valid password.'),
            'required': _('Your password is required.')
        }

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if (self.user_cache is None):
                raise forms.ValidationError(self.message_incorrect_password)
            if not self.user_cache.is_active:
                raise forms.ValidationError(self.message_inactive)
        self.check_for_test_cookie()
        return self.cleaned_data


class RegistrationForm(forms.Form):
    bad_domains = (
        'aim.com', 'aol.com', 'email.com', 'hushmail.com', 'mail.ru',
        'mailinator.com', 'live.com'
    )

    email = forms.EmailField(required=True, error_messages={
        'invalid': _('Please enter a valid email address.'),
        'required': _('Your email address is required.')
    })

    password1 = forms.CharField(required=True, error_messages={
        'required': _('A password is required.')
    })

    password2 = forms.CharField(required=True, error_messages={
        'required': _('A confirmation password is required.')
    })

    privacy = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'required'}),
        label=_(u'I have read and agree to the Privacy Policy'),
        required=True,
        error_messages={
            'required': _('You must agree to the privacy policy to register.')
        })

    tos = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'required'}),
        label=_(u'I have read and agree to the Terms of Service'),
        required=True,
        error_messages={
            'required': _('You must agree to the terms to register.')
        })

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        email = self.cleaned_data['email']

        if get_user_model().objects.filter(email__iexact=email):
            raise forms.ValidationError(
                _('This email address is already in use. Please supply a '
                  'different email address.')
            )

        address, domain = email.split('@')

        if domain in self.bad_domains:
            raise forms.ValidationError(_(
                'Email addresses from "%s" may not be used to register for an '
                'account.'
                % domain
            ))

        return email

    def clean(self):
        """
        Validates that password1 and password2 match.
        """
        cleaned_data = super(RegistrationForm, self).clean()

        if not ('password1' in cleaned_data and
                'password2' in cleaned_data and
                cleaned_data['password1'] == cleaned_data['password2']):
            raise forms.ValidationError(_('The passwords given do not match!'))

        return cleaned_data

    def save(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']

        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        key_expiration = now() + timedelta(
            days=getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', 7)
        )

        key = ActivationKey.objects.create(user=user, expires=key_expiration)
        key.send_email()

        return user, key
