# coding: utf8

from django.conf import settings
from django.db import models
from django.utils import timezone

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django_extensions.db.models import TimeStampedModel

from coreutils.email import send_email
from coreutils.models import ExpiringModel, KeyedModel, RenderableModel
from coreutils.site import get_default_site_url


class ActivationKey(ExpiringModel, KeyedModel, RenderableModel):
    template_name = 'registration/activation_email.txt'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='activation_keys'
    )

    class Meta:
        app_label = 'authentication'

    class KeyExpired(Exception):
        pass

    @classmethod
    def Activate(cls, key):
        """
        Gets the ActivationKey and calls activate on it. If the key is expired
        KeyExpired will be raised, if the key does not exist DoesNotExist will
        be raised, or returning True if successful.
        """
        instance = cls.objects.get(key=key)

        if instance.expires <= timezone.now():
            instance.delete()
            raise ActivationKey.KeyExpired()

        instance.activate()

        return True

    def activate(self):
        """
        Sets the `is_active` attribute of the referenced user to True, saves
        the referenced user model and deletes this instance of ActivationKey
        """

        self.user.is_active = True
        self.user.save()
        self.delete()

    def get_email_subject(self):
        """ Returns 'Activate your account!' """
        return getattr(
            settings, 'ACTIVATION_EMAIL_SUBJECT', 'Activate your account!'
        )
    email_subject = property(get_email_subject)

    def get_context_data(self):
        return {
            'activation_key': self.key,
            'expiration_days': getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', 7),
            'site': get_default_site_url(),
        }

    def get_template_name(self):
        """
        Returns the value declared in settings.ACTIVATION_EMAIL_TEMPLATE,
        defaulting to 'authentication/activation_email.txt' if not found.
        """
        return getattr(
            settings,
            'ACTIVATION_EMAIL_TEMPLATE',
            'authentication/activation_email.txt'
        )
    template_name = property(get_template_name)

    def send_email(self):
        """
        Sends an email to the user associated with this ActivationKey instance
        containing the link used to activate the user account.
        """
        return send_email(
            self.email_subject,
            self.render(self.template_name),
            settings.ACTIVATION_EMAIL_SENDER,
            (self.user.email,)
        )


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        email = UserManager.normalize_email(email)
        user = self.model(email=email, password=None, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    display_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)

    REQUIRED_FIELDS = ('display_name',)
    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        app_label = 'authentication'

    def get_full_name(self):
        return self.display_name
    full_name = property(get_full_name)

    def get_is_staff(self):
        return self.is_superuser
    is_staff = property(get_is_staff)

    def get_short_name(self):
        return self.display_name
    short_name = property(get_short_name)

    def get_username(self):
        return self.email
    username = property(get_username)
