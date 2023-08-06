from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from googletools.models import AnalyticsCode, SiteVerificationCode


class AnalyticsCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'site')


class SiteVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'site')


admin.site.register(AnalyticsCode, AnalyticsCodeAdmin)
admin.site.register(SiteVerificationCode, SiteVerificationCodeAdmin)
