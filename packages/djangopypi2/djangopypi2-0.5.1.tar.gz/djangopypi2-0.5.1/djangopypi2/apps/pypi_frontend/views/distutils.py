import os,re
from logging import getLogger

from django.conf import settings
from django.db import transaction
from django.http import *
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import MultiValueDict
from django.contrib.auth import login

from ...pypi_config.models import Classifier
from ...pypi_config.models import DistributionType
from ...pypi_config.models import PythonVersion
from ..metadata import METADATA_FIELDS
from ..decorators import basic_auth
from ..forms import PackageForm, ReleaseForm
from ..models import Package
from ..models import Release
from ..models import Distribution

log = getLogger(__name__)

ALREADY_EXISTS_FMT = _(
    "A file named '%s' already exists for %s. Please create a new release.")

@basic_auth
@transaction.commit_manually
def register_or_upload(request):
    if request.method != 'POST':
        transaction.rollback()
        return HttpResponseBadRequest('Only post requests are supported')
    
    name = request.POST.get('name',None).strip()
    
    if not name:
        transaction.rollback()
        return HttpResponseBadRequest('No package name specified')
    
    try:
        package = Package.objects.get(name=name)
    except Package.DoesNotExist:
        package = Package.objects.create(name=name)
        package.owners.add(request.user)
    
    if (request.user not in package.owners.all() and 
        request.user not in package.maintainers.all()):
        
        transaction.rollback()
        return HttpResponseForbidden('You are not an owner/maintainer of %s' % (package.name,))
    
    version = request.POST.get('version',None).strip()
    metadata_version = request.POST.get('metadata_version', None).strip()
    
    if not version or not metadata_version:
        transaction.rollback()
        return HttpResponseBadRequest('Release version and metadata version must be specified')
    
    if not metadata_version in METADATA_FIELDS:
        transaction.rollback()
        return HttpResponseBadRequest('Metadata version must be one of: %s' 
                                      (', '.join(METADATA_FIELDS.keys()),))
    
    release, created = Release.objects.get_or_create(package=package,
                                                     version=version)
    
    if (('classifiers' in request.POST or 'download_url' in request.POST) and 
        metadata_version == '1.0'):
        metadata_version = '1.1'
    
    release.metadata_version = metadata_version
    
    fields = METADATA_FIELDS[metadata_version]
    
    if 'classifiers' in request.POST:
        request.POST.setlist('classifier',request.POST.getlist('classifiers'))
    
    release.package_info = MultiValueDict(dict(filter(lambda t: t[0] in fields,
                                                      request.POST.iterlists())))
    
    for key, value in release.package_info.iterlists():
        release.package_info.setlist(key,
                                     filter(lambda v: v != 'UNKNOWN', value))
    
    release.save()
    if not 'content' in request.FILES:
        transaction.commit()
        return HttpResponse('release registered')
    
    uploaded = request.FILES.get('content')
    
    for dist in release.distributions.all():
        if os.path.basename(dist.content.name) == uploaded.name:
            """ Need to add handling optionally deleting old and putting up new """
            transaction.rollback()
            return HttpResponseBadRequest('That file has already been uploaded...')

    md5_digest = request.POST.get('md5_digest','')
    
    try:
        filetype, created = DistributionType.objects.get_or_create(key=request.POST.get('filetype','sdist'))
        if created:
            filetype.name = filetype.key
            filetype.save()

        textual_pyversion = request.POST.get('pyversion','')
        if textual_pyversion == '':
            pyversion = None
        else:
            major, minor = (int(x) for x in textual_pyversion.split('.'))
            pyversion, created = PythonVersion.objects.get_or_create(major=major, minor=minor)
            if created:
                pyversion.save()

        new_file = Distribution.objects.create(release=release,
                                               content=uploaded,
                                               filetype=filetype,
                                               pyversion=pyversion,
                                               uploader=request.user,
                                               comment=request.POST.get('comment',''),
                                               signature=request.POST.get('gpg_signature',''),
                                               md5_digest=md5_digest)
    except Exception, e:
        transaction.rollback()
        log.exception('Error when storing upload: %s', e)
        return HttpResponseServerError('Failure when storing upload')
    
    transaction.commit()
    
    return HttpResponse('upload accepted')

def list_classifiers(request, mimetype='text/plain'):
    response = HttpResponse(mimetype=mimetype)
    response.write(u'\n'.join(map(lambda c: c.name,Classifier.objects.all())))
    return response
