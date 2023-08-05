from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView

from .mixins import cbv


def auth_view_factory(view, *mixins):
    """
    Dynamically produce a view that incorporates the AuthenticatedViewMixin
    along with any extra mixins that you may require.
    """
    inherit = (cbv.AuthenticatedViewMixin,) + mixins + (view,)
    return type(view.__name__, inherit, {})


AuthTemplateView = auth_view_factory(TemplateView)

AuthDetailView = auth_view_factory(DetailView)

AuthCreateView = auth_view_factory(CreateView)
AuthFormView = auth_view_factory(FormView)
AuthUpdateView = auth_view_factory(UpdateView)

AuthListView = auth_view_factory(ListView)
