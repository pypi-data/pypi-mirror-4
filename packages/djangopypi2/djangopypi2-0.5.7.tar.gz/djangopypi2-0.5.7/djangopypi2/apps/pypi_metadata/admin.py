from django.contrib import admin
from . import models

admin.site.register(models.Classifier)
admin.site.register(models.PythonVersion)
admin.site.register(models.PlatformName)
admin.site.register(models.Architecture)
admin.site.register(models.DistributionType)
