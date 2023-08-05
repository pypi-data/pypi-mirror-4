import logging
from os.path import basename
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from ..pypi_metadata.definitions import METADATA_VERSIONS
from .models import Package, Release, Distribution

log = logging.getLogger(__name__)

class SimplePackageSearchForm(forms.Form):
    query = forms.CharField(max_length=255)

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        exclude = ['name']

class DistributionUploadForm(forms.ModelForm):
    class Meta:
        model = Distribution
        fields = ('content','comment','filetype','pyversion',)
        
    def clean_content(self):
        content = self.cleaned_data['content']
        storage = self.instance.content.storage
        field = self.instance.content.field
        
        name = field.generate_filename(instance=self.instance,
                                       filename=content.name)
        
        if not storage.exists(name):
            log.error('%s does not exist', name)
            return content
        
        if settings.DJANGOPYPI_ALLOW_VERSION_OVERWRITE:
            raise forms.ValidationError('Version overwrite is not yet handled')
        
        raise forms.ValidationError('That distribution already exists, please '
                                    'delete it first before uploading a new '
                                    'version.')

class ReleaseForm(forms.ModelForm):
    metadata_version = forms.CharField(widget=forms.Select(choices=zip(METADATA_VERSIONS.keys(),
                                                                       METADATA_VERSIONS.keys())))
    
    class Meta:
        model = Release
        exclude = ['package', 'version', 'package_info']
