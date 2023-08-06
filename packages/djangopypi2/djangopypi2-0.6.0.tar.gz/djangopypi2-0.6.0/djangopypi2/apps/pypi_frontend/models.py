from django.db import models
from django.utils.translation import ugettext_lazy as _

class MirrorSite(models.Model):
    enabled = models.BooleanField(default=False)
    name = models.CharField(max_length=64)
    url = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

class MirrorLog(models.Model):
    mirror_site = models.ForeignKey(MirrorSite, related_name='logs')
    created = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.action
    
    class Meta:
        get_latest_by = 'created'
