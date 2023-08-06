# coding: utf8

from django.conf import settings

from coreutils.models import get_model_class


def get_user_model():
    """
    Returns the user model class for the user model declared as AUTH_USER_MODEL
    in settings.py
    """

    return get_model_class(settings.AUTH_USER_MODEL)
