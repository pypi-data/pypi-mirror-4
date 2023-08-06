# coding: utf8

from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url('accounts/profile',
        TemplateView.as_view(template_name='test_index.html'),
        name='home'),
    url(r'', include('authentication.urls')),
)
