from django.conf import settings
from django.contrib import admin
from . import models

admin.site.register(models.Configuration)
admin.site.register(models.Package)
admin.site.register(models.Release)
admin.site.register(models.Distribution)
admin.site.register(models.Review)
