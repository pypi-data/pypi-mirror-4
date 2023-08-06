from logging import getLogger
from django.conf import settings
from django.http import HttpResponseNotAllowed

from ..decorators import csrf_exempt
from ..http import parse_distutils_request
from ..models import Package, Release
from .xmlrpc import parse_xmlrpc_request
from . import releases
from . import distutils

log = getLogger(__name__)
    
ACTION_VIEWS = {
    "file_upload": distutils.register_or_upload, #``sdist`` command
    "submit": distutils.register_or_upload, #``register`` command
    "list_classifiers": distutils.list_classifiers, #``list_classifiers`` command
}

@csrf_exempt
def root(request, **kwargs):
    """ Root view of the package index, handle incoming actions from distutils
    or redirect to a more user friendly view """
    if request.method == 'POST':
        if request.META['CONTENT_TYPE'] == 'text/xml':
            log.debug('XMLRPC request received')
            return parse_xmlrpc_request(request)
        log.debug('Distutils request received')
        parse_distutils_request(request)
        action = request.POST.get(':action','')
    else:
        action = request.GET.get(':action','')
    
    if not action:
        log.debug('No action in root view')
        return releases.index(request, **kwargs)
    
    if not action in ACTION_VIEWS:
        log.error('Invalid action encountered: %s' % (action,))
        return HttpResponseNotAllowed(settings.DJANGOPYPI_ACTION_VIEW.keys())

    log.debug('Applying configured action view for %s' % (action,))
    return ACTION_VIEWS[action](request, **kwargs)

