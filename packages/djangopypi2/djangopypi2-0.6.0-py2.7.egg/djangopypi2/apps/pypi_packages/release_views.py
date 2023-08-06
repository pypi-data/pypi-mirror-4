from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.forms.models import inlineformset_factory
from django.http import Http404
from django.http import HttpResponseRedirect
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from ..pypi_ui.shortcuts import render_to_response
from .mixins import UserOwnsPackage, UserMaintainsPackage
from .decorators import user_maintains_package
from .models import Package
from .models import Release
from .models import Distribution
from .forms import ReleaseForm
from .forms import DistributionUploadForm
from ..pypi_metadata.forms import METADATA_FORMS

class SingleReleaseMixin(SingleObjectMixin):
    model = Release
    slug_field = 'version'
    slug_url_kwarg = 'version'
    context_object_name = 'release'

    def get_queryset(self):
        return self.model.objects.filter(package__name=self.kwargs['package_name'])

class ReleaseDetails(SingleReleaseMixin, DetailView):
    template_name = 'pypi_packages/release_detail.html'

class DeleteRelease(SingleReleaseMixin, DeleteView, UserOwnsPackage):
    success_url = reverse_lazy('djangopypi2-packages-index')

class ManageRelease(SingleReleaseMixin, UpdateView, UserMaintainsPackage):
    template_name = 'pypi_packages/release_manage.html'
    form_class = ReleaseForm

def _get_release(request, package_name, version):
    release = get_object_or_404(Package, name=package_name).get_release(version)
    if not release:
        raise Http404('Version %s does not exist for %s' % (version, package_name))
    return release

@user_maintains_package()
def manage_metadata(request, package_name, version):
    release = _get_release(request, package_name, version)

    if not release.metadata_version in METADATA_FORMS:
        #TODO: Need to change this to a more meaningful error
        raise Http404()

    form_class = METADATA_FORMS.get(release.metadata_version)
    
    initial = {}
    multivalue = ('classifier',)
    
    for key, values in release.package_info.iterlists():
        if key in multivalue:
            initial[key] = values
        else:
            initial[key] = '\n'.join(values)
    
    if request.method == 'POST':
        form = form_class(data=request.POST, initial=initial)
        
        if form.is_valid():
            for key, value in form.cleaned_data.iteritems():
                if isinstance(value, basestring):
                    release.package_info[key] = value
                elif hasattr(value, '__iter__'):
                    release.package_info.setlist(key, list(value))
            
            release.save()
            return create_update.redirect(None, release)
    else:
        form = form_class(initial=initial)

    return render_to_response(
        'pypi_packages/release_manage.html',
        dict(release=release, form=form),
        context_instance = RequestContext(request),
        mimetype         = settings.DEFAULT_CONTENT_TYPE,
    )

@user_maintains_package()
def manage_files(request, package_name, version):
    release = _get_release(request, package_name, version)
    formset_factory = inlineformset_factory(Release, Distribution, fields=('comment', ), extra=0)

    if request.method == 'POST':
        formset = formset_factory(data=request.POST,
                                  files=request.FILES,
                                  instance=release)
        if formset.is_valid():
            formset.save()
            formset = formset_factory(instance=release)
    else:
        formset = formset_factory(instance=release)

    return render_to_response(
        'pypi_packages/release_manage_files.html',
        dict(release=release, formset=formset, upload_form=DistributionUploadForm()),
        context_instance = RequestContext(request),
        mimetype         = settings.DEFAULT_CONTENT_TYPE,
    )

@user_maintains_package()
def upload_file(request, package_name, version):
    release = _get_release(request, package_name, version)
    
    if request.method == 'POST':
        form = DistributionUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            dist = form.save(commit=False)
            dist.release = release
            dist.uploader = request.user
            dist.save()
            
            return create_update.redirect(
                reverse_lazy('djangopypi2-release-manage-files',
                        kwargs=dict(package_name=package_name, version=version)),
                release)
    else:
        form = DistributionUploadForm()

    return render_to_response(
        'pypi_packages/release_upload_file.html',
        dict(release=release, form=form),
        context_instance = RequestContext(request),
        mimetype         = settings.DEFAULT_CONTENT_TYPE,
    )
