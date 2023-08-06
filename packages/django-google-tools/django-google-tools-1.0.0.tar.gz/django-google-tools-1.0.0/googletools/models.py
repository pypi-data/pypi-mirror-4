from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AnalyticsCode(models.Model):
    site = models.ForeignKey(Site, verbose_name=_('site'), unique=True)
    code = models.CharField(_('code'), max_length=100)
    speed = models.BooleanField(verbose_name=_('track speed'), default=False)
    
    def __unicode__(self):
        return self.code
    
    class Meta:
        ordering = ('site', 'code')
        verbose_name = _('analytics code')
        verbose_name_plural = _('analytics codes')


class SiteVerificationCode(models.Model):
    site = models.ForeignKey(Site, verbose_name=_('site'), unique=True)
    code = models.CharField(_('code'), max_length=100)
    
    def __unicode__(self):
        return self.code
    
    class Meta:
        ordering = ('site', 'code')
        verbose_name = _('site verification code')
        verbose_name_plural = _('site verification codes')
