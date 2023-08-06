# coding: utf8

import re

from django.conf import settings
from django.contrib.auth import get_user_model
create_user = get_user_model().objects.create_user

from django.core import mail

from testutils import BaseTestCase


class TestPassword(BaseTestCase):
    urls = 'authentication.test_urls'

    # def test_password_change_template_used(self):
    #     self.check_template(
    #         'password_change',
    #         'authentication/password_change_form.html'
    #     )

    # def test_password_change_done_template_used(self):
    #     self.check_template(
    #         'password_change_done',
    #         'authentication/password_change_done.html'
    #     )

    def test_password_reset_template_used(self):
        self.check_template(
            'password_reset',
            'authentication/password_reset_form.html'
        )

    def test_password_reset_done_template_used(self):
        self.check_template(
            'password_reset_done',
            'authentication/password_reset_done.html',
        )

    def test_password_reset_confirm_template_used(self):
        self.check_template(
            'password_reset_confirm',
            'authentication/password_reset_confirm.html',
            uidb36='1',
            token='1-1',
        )

    def test_password_reset_complete_template_used(self):
        self.check_template(
            'password_reset_complete',
            'authentication/password_reset_complete.html'
        )

    def setUp(self):
        self.user = create_user('valid@example.com', 'test', is_active=True)

    def test_change(self):
        response = self.post(
            'login',
            client='client1', data={
                'email': self.user.email,
                'password': 'test',
            }, follow=True,
        )

        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)

        response = self.post(
            'password_change',
            client='client1', data={
                'old_password': 'test',
                'new_password1': 'hamster',
                'new_password2': 'hamster',
            }, follow=True,
        )

        self.assertContains(response, 'Your password was changed!')
        self.assertTrue(self.login(
            'client2', email=self.user.email, password='hamster'
        ))

    def test_reset(self):
        response = self.post(
            'password_reset', data={
                'email': self.user.email,
            }, follow=True,
        )

        self.assertContains(response, 'Check your email!')

        token_regex = re.compile(
            r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})'
        )

        uid, token = token_regex.findall(mail.outbox[0].body)[0].split('-', 1)

        response = self.get(
            'password_reset_confirm',
            url_kwargs={
                'uidb36': uid,
                'token': token,
            }
        )

        self.assertContains(response, 'Enter Your New Password.')

        response = self.post(
            'password_reset_confirm',
            url_kwargs={
                'uidb36': uid,
                'token': token,
            }, data={
                'new_password1': 'test',
                'new_password2': 'test',
            }, follow=True,
        )

        self.assertContains(response, 'Password Reset Successfully!')
        self.assertTrue(self.login(
            'client2', email=self.user.email, password='test'
        ))
