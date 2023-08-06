# coding: utf8

import re

from django.core import mail
from django.test.utils import override_settings

from testutils import BaseTestCase


class TestSignup(BaseTestCase):
    email = 'test@example.com'
    password = 'test'

    def test_registration_activation_complete_template_used(self):
        self.check_template(
            'account_activation_complete',
            'authentication/activation_complete.html'
        )

    def test_registration_activate_template_used(self):
        self.check_template(
            'account_activate',
            'authentication/activate.html',
            activation_key='a'
        )

    def test_account_register_template_used(self):
        self.check_template(
            'account_register',
            'authentication/registration_form.html'
        )

    def test_registration_complete_template_used(self):
        self.check_template(
            'account_registration_complete',
            'authentication/registration_complete.html'
        )

    def test_registration_disallowed_template_used(self):
        self.check_template(
            'account_registration_disallowed',
            'authentication/registration_closed.html'
        )

    @override_settings(ACTIVATION_EMAIL_SENDER='test@example.com')
    def test_signup_valid(self):
        response = self.post(
            'account_register', data={
                'email': self.email,
                'password1': self.password,
                'password2': self.password,
                'privacy': 'on',
                'tos': 'on',
            }, follow=True,
        )

        self.assertContains(response, 'Check your email!')

        activation_url = self.get_url(
            'account_activate', activation_key='a'
        )[:-1]

        key_regex = re.compile(r'%s(\w+)' % activation_url)

        key = key_regex.findall(mail.outbox[0].body)[0]

        response = self.get(
            'account_activate',
            url_kwargs={'activation_key': key},
            follow=True,
        )

        self.assertContains(response, 'Your account is now activated!')
        self.assertTrue(self.email, self.password)

    def test_signup_invalid_email(self):
        response = self.post(
            'account_register', data={
                'email': self.email.split('@')[0],
                'password1': self.password,
                'password2': self.password,
                'privacy': 'on',
                'tos': 'on',
            }, follow=True,
        )

        self.assertContains(response, 'Please enter a valid email address.')

    def test_signup_no_email(self):
        response = self.post(
            'account_register', data={
                'password1': self.password,
                'password2': self.password,
                'privacy': 'on',
                'tos': 'on',
            }, follow=True,
        )

        self.assertContains(response, 'Your email address is required.')

    def test_signup_no_password(self):
        response = self.post(
            'account_register', data={
                'email': self.email,
                'password2': self.password,
                'privacy': 'on',
                'tos': 'on',
            }, follow=True,
        )

        self.assertContains(response, 'A password is required.')

    def test_signup_no_password_confirmation(self):
        response = self.post(
            'account_register', data={
                'email': self.email,
                'password1': self.password,
                'privacy': 'on',
                'tos': 'on',
            }, follow=True,
        )

        self.assertContains(response, 'A confirmation password is required.')

    def test_signup_no_tos(self):
        response = self.post(
            'account_register', data={
                'email': self.email,
                'password1': self.password,
                'password2': self.password,
                'privacy': 'on',
            }, follow=True,
        )

        self.assertContains(
            response, 'You must agree to the terms to register.'
        )

    def test_signup_no_privacy(self):
        response = self.post(
            'account_register', data={
                'email': self.email,
                'password1': self.password,
                'password2': self.password,
                'tos': 'on',
            }, follow=True,
        )

        self.assertContains(
            response, 'You must agree to the privacy policy to register.'
        )
