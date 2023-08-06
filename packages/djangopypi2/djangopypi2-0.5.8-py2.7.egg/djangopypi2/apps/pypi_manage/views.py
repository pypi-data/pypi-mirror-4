from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from ..pypi_ui.shortcuts import render_to_response

def _administrator_required(func):
    @login_required
    def _decorator(request, *args, **kwargs):
        if not request.user.is_staff:
            return render_to_response('pypi_manage/forbidden.html', context_instance=RequestContext(request))
        return func(request, *args, **kwargs)
    return _decorator

@_administrator_required
def index(request):
    return render_to_response('pypi_manage/index.html', context_instance=RequestContext(request))
