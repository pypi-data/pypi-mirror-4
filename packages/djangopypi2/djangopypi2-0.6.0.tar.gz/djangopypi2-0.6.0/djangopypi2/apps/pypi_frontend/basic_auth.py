from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login

try:
    from functools import wraps, WRAPPER_ASSIGNMENTS
except ImportError:
    from django.utils.functional import wraps, WRAPPER_ASSIGNMENTS

try:
    from django.utils.decorators import available_attrs
except ImportError:
    def available_attrs(fn):
        return tuple(a for a in WRAPPER_ASSIGNMENTS if hasattr(fn, a))

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

    def __init__(self, realm):
        HttpResponse.__init__(self)
        self['WWW-Authenticate'] = 'Basic realm="%s"' % realm

def _login_basic_auth(request):
    authentication = request.META.get("HTTP_AUTHORIZATION")
    if not authentication:
        return
    (authmeth, auth) = authentication.split(' ', 1)
    if authmeth.lower() != "basic":
        return
    auth = auth.strip().decode("base64")
    username, password = auth.split(":", 1)
    return authenticate(username=username, password=password)

def basic_auth(view_func):
    """ Decorator for views that need to handle basic authentication such as
    distutils views. """

    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        user = _login_basic_auth(request)

        if not user:
            return HttpResponseUnauthorized('pypi')

        login(request, user)
        if not request.user.is_authenticated():
            return HttpResponseForbidden("Not logged in, or invalid username/"
                                         "password.")
        return view_func(request, *args, **kwargs)
    return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
