from django.contrib import admin
from leech.models import *


class ShortenUrlAdmin(admin.ModelAdmin):
    list_display = ['source_url', 'slug', 'create_time']


class ClickLogAdmin(admin.ModelAdmin):
    list_display = ['shorten_url', 'remote_address']


class ClickLogAttributeAdmin(admin.ModelAdmin):
    list_display = ['click_log', 'name', 'value']

admin.site.register(ShortenUrl, ShortenUrlAdmin)
admin.site.register(ClickLog, ClickLogAdmin)
admin.site.register(ClickLogAttribute, ClickLogAttributeAdmin)