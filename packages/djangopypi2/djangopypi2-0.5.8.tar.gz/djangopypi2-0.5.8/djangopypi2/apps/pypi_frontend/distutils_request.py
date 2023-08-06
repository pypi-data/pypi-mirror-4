from logging import getLogger
from django.http import QueryDict
from django.http import HttpResponseNotAllowed
from django.utils.datastructures import MultiValueDict
from django.core.files.uploadedfile import TemporaryUploadedFile
from .distutils_views import ACTION_VIEWS

log = getLogger(__name__)

def _get_distutils_action(request):
    if request.method == 'POST':
        parse_distutils_request(request)
        action = request.POST.get(':action', None)
    else:
        action = request.GET.get(':action', None)
    return action

def is_distutils_request(request):
    return _get_distutils_action(request) is not None

def handle_distutils_request(request):
    action = _get_distutils_action(request)

    if action not in ACTION_VIEWS:
        log.error('Invalid action encountered: %r', action)
        return HttpResponseNotAllowed(ACTION_VIEWS.keys())

    return ACTION_VIEWS[action](request)

def _parse_header(header):
    headers = {}
    for kvpair in filter(lambda p: p,
                         map(lambda p: p.strip(),
                             header.split(';'))):
        try:
            key, value = kvpair.split("=",1)
        except ValueError:
            continue
        headers[key.strip()] = value.strip('"')
    
    return headers

def parse_distutils_request(request):
    """ This is being used because the built in request parser that Django uses,
    django.http.multipartparser.MultiPartParser is interperting the POST data
    incorrectly and/or the post data coming from distutils is invalid.
    
    One portion of this is the end marker: \r\n\r\n (what Django expects) 
    versus \n\n (what distutils is sending). 
    """
    try:
        sep = request.raw_post_data.splitlines()[1]
    except:
        raise ValueError('Invalid post data')

    request.POST = QueryDict('',mutable=True)
    try:
        request._files = MultiValueDict()
    except Exception, e:
        pass
    
    for part in filter(lambda e: e.strip(), request.raw_post_data.split(sep)):
        try:
            header, content = part.lstrip().split('\n',1)
        except Exception, e:
            continue
        
        if content.startswith('\n'):
            content = content[1:]
        
        if content.endswith('\n'):
            content = content[:-1]
        
        headers = _parse_header(header)
        
        if "name" not in headers:
            continue
        
        if "filename" in headers:
            dist = TemporaryUploadedFile(name=headers["filename"],
                                         size=len(content),
                                         content_type="application/gzip",
                                         charset='utf-8')
            dist.write(content)
            dist.seek(0)
            request.FILES.appendlist(headers['name'], dist)
        else:
            request.POST.appendlist(headers["name"],content)
    return
