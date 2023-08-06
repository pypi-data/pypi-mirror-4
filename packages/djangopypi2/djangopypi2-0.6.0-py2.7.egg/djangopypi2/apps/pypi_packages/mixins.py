from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

class UserOwnsPackage(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        super(UserOwnsPackage, self).dispatch(*args, **kwargs)

class UserMaintainsPackage(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        super(UserMaintainsPackage, self).dispatch(*args, **kwargs)
