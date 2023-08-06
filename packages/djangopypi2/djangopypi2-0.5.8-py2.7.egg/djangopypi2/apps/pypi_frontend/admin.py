from django.contrib import admin
from . import models

admin.site.register(models.MirrorSite)
admin.site.register(models.MirrorLog)
