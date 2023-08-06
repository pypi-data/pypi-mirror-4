from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.query import Q
from django.http import Http404, HttpResponseRedirect
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.views.generic import list_detail
from django.views.generic import create_update
from ..pypi_ui.shortcuts import render_to_response
from .decorators import user_owns_package
from .decorators import user_maintains_package
from .models import Package
from .models import Release
from .forms import SimplePackageSearchForm
from .forms import PackageForm

def index(request):
    return list_detail.object_list(request, template_object_name='package', queryset=Package.objects.all())

def details(request, package_name):
    return list_detail.object_detail(
        request,
        object_id            = package_name,
        template_object_name = 'package',
        queryset             = Package.objects.all(),
    )

def search(request):
    if request.method == 'POST':
        form = SimplePackageSearchForm(request.POST)
    else:
        form = SimplePackageSearchForm(request.GET)

    if form.is_valid():
        q = form.cleaned_data['query']

    return list_detail.object_list(
        request,
        template_object_name = 'package',
        queryset             = Package.objects.filter(Q(name__contains=q) | 
                                                      Q(releases__package_info__contains=q)).distinct())

@user_owns_package()
def manage(request, package_name):
    return create_update.update_object(
        request,
        object_id            = package_name,
        form_class           = PackageForm,
        template_name        = 'pypi_packages/package_manage.html',
        template_object_name = 'package',
    )

@user_maintains_package()
def manage_versions(request, package_name):
    package = get_object_or_404(Package, name=package_name)
    kwargs.setdefault('formset_factory_kwargs', {})
    kwargs['formset_factory_kwargs'].setdefault('fields', ('hidden',))
    kwargs['formset_factory_kwargs']['extra'] = 0

    kwargs.setdefault('formset_factory', inlineformset_factory(Package, Release, **kwargs['formset_factory_kwargs']))
    kwargs.setdefault('template_name', 'pypi_packages/package_manage_versions.html')
    kwargs.setdefault('template_object_name', 'package')
    kwargs.setdefault('extra_context',{})
    kwargs.setdefault('mimetype',settings.DEFAULT_CONTENT_TYPE)
    kwargs['extra_context'][kwargs['template_object_name']] = package_name
    kwargs.setdefault('formset_kwargs',{})
    kwargs['formset_kwargs']['instance'] = package_name

    if request.method == 'POST':
        formset = kwargs['formset_factory'](data=request.POST, **kwargs['formset_kwargs'])
        if formset.is_valid():
            formset.save()
            return create_update.redirect(kwargs.get('post_save_redirect', None),
                                          package_name)

    formset = kwargs['formset_factory'](**kwargs['formset_kwargs'])

    kwargs['extra_context']['formset'] = formset

    return render_to_response(kwargs['template_name'], kwargs['extra_context'],
                              context_instance=RequestContext(request),
                              mimetype=kwargs['mimetype'])
