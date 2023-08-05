from django.contrib import admin
from . import models

admin.site.register(models.Classifier)
admin.site.register(models.GlobalConfiguration)
admin.site.register(models.PythonVersion)
admin.site.register(models.PlatformName)
admin.site.register(models.Architecture)
admin.site.register(models.DistributionType)
admin.site.register(models.MirrorSite)
admin.site.register(models.MirrorLog)

