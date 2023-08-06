# coding: utf8

from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'display_name',
        'is_active',
        'is_staff',
        'is_superuser',
        'created',
        'modified',
    )

admin.site.register(User, UserAdmin)
