from django.db import models
from django.utils.translation import ugettext_lazy as _

class Classifier(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

    class Meta:
        verbose_name = _(u"classifier")
        verbose_name_plural = _(u"classifiers")
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class GlobalConfigurationManager(models.Manager):
    def latest(self):
        try:
            return super(GlobalConfigurationManager, self).latest()
        except GlobalConfiguration.DoesNotExist:
            global_configuration = GlobalConfiguration()
            global_configuration.save()
            return global_configuration

class GlobalConfiguration(models.Model):
    '''Stores the configuration of this site. As a rule, the most
    recent configuration is always used, and past configurations
    are kept for reference and for rollback.
    '''
    objects = GlobalConfigurationManager()

    timestamp = models.DateTimeField(auto_now_add=True)
    allow_version_overwrite = models.BooleanField(default=False)
    upload_directory = models.CharField(max_length=256, default='dists',
        help_text='Direcory relative to MEDIA_ROOT in which user uploads are kept')

    class Meta:
        ordering = ('-timestamp', )
        verbose_name = _(u'global configuration')
        verbose_name_plural = _(u'global configurations')
        get_latest_by = 'timestamp'

class PythonVersion(models.Model):
    major = models.IntegerField()
    minor = models.IntegerField()

    class Meta:
        ordering = ('major', 'minor')
        verbose_name = _(u'python version')
        verbose_name_plural = _(u'python versions')
        unique_together = ('major', 'minor')

    def __unicode__(self):
        return '%s.%s' % (self.major, self.minor)

class PlatformName(models.Model):
    key = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = _(u'platform name')
        verbose_name_plural = _(u'platform names')
        ordering = ('name', )

    def __unicode__(self):
        return self.name

class Architecture(models.Model):
    key = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = _(u'architecture')
        verbose_name_plural = _(u'architectures')
        ordering = ('name', )

    def __unicode__(self):
        return self.name

class DistributionType(models.Model):
    key = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = _(u'distribution type')
        verbose_name_plural = _(u'distribution types')
        ordering = ('name', )

    def __unicode__(self):
        return self.name

class MirrorSite(models.Model):
    POLICIES = ('Duplicate', 'Redirect')
 
    enabled = models.BooleanField(default=False)
    name = models.CharField(max_length=64)
    url = models.CharField(max_length=255, unique=True)
    policy = models.CharField(max_length=16, default=POLICIES[0], choices=zip(POLICIES, POLICIES))

    def __unicode__(self):
        return self.name

class MirrorLog(models.Model):
    mirror_site = models.ForeignKey(MirrorSite, related_name='logs')
    created = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=256)
    
    def __unicode__(self):
        return '%s (%s)' % (self.master, str(self.created))
    
    class Meta:
        get_latest_by = 'created'
