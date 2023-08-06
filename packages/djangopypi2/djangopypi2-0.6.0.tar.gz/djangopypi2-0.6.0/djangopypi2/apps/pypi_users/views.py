from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

class SingleUserMixin(SingleObjectMixin):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Index, self).dispatch(*args, **kwargs)

class MultipleUsersMixin(MultipleObjectMixin):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'users'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Index, self).dispatch(*args, **kwargs)

class Index(MultipleUsersMixin, ListView):
    template_name = 'pypi_users/index.html'

class UserDetails(SingleUserMixin, DetailView):
    template_name = 'pypi_users/user_profile.html'

@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')
