# coding: utf8

from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView
)

from braces.views import LoginRequiredMixin


class ProtectedCreateView(LoginRequiredMixin, CreateView):
    pass


class ProtectedDeleteView(LoginRequiredMixin, DeleteView):
    pass


class ProtectedFormView(LoginRequiredMixin, FormView):
    pass


class ProtectedListView(LoginRequiredMixin, ListView):
    pass


class ProtectedTemplateView(LoginRequiredMixin, TemplateView):
    pass


class ProtectedUpdateView(LoginRequiredMixin, UpdateView):
    pass
