# coding: utf8

from django.conf import settings
from django.contrib.auth import get_user_model
create_user = get_user_model().objects.create_user

from testutils import BaseTestCase


class TestLogin(BaseTestCase):
    urls = 'authentication.test_urls'

    def test_login_template_used(self):
        self.check_template(
            'login', 'authentication/login.html'
        )

    def test_logout_template_used(self):
        self.check_template(
            'logout', 'authentication/logged_out.html'
        )

    def test_valid_user(self):
        user = create_user('valid@example.com', 'test', is_active=True)

        response = self.post(
            'login', data={
                'email': user.email,
                'password': 'test',
            }, follow=True,
        )

        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)

    def test_invalid_user(self):
        response = self.post(
            'login', data={
                'email': 'samantha@dundermifflin.com',
                'password': 'test',
            }
        )

        self.assertContains(
            response, 'Please enter a correct email and password.'
        )

    def test_inactive_user(self):
        user = create_user('inactive@example.com', 'test', is_active=True)
        user.is_active = False
        user.save()

        response = self.post(
            'login', data={
                'email': user.email,
                'password': 'test',
            }
        )

        self.assertContains(
            response, 'Your account is inactive.'
        )

    def test_no_email(self):
        response = self.post(
            'login', data={
                'password': 'test',
            }
        )

        self.assertContains(response, 'Your email is required.')

    def test_no_password(self):
        response = self.post(
            'login', data={
                'email': 'test@example.com',
            }
        )

        self.assertContains(response, 'Your password is required.')
