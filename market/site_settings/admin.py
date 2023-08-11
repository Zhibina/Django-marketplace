from django.contrib import admin
from .models import SiteSettings


class SiteSettingsAdmin(admin.ModelAdmin):
    change_form_template = 'market/site_settings/settings.html'


admin.site.register(SiteSettings, SiteSettingsAdmin)
