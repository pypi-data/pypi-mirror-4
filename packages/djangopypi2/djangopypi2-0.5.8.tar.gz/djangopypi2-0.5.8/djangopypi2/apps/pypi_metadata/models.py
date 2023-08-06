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
