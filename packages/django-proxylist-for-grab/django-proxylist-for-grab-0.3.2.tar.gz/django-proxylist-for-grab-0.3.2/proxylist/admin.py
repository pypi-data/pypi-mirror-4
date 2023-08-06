# -*- coding: utf-8 -*-

from django.contrib import admin
from django.conf import settings

from proxylist.models import Proxy, Mirror, ProxyCheckResult


class ProxyAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'port', 'country', 'anonymity_level',
                    'proxy_type', 'last_check', 'errors',)
    list_filter = ('anonymity_level', 'proxy_type', 'country',)
    search_fields = ('=hostname', '=port', 'country',)
    list_per_page = 25


class ProxyCheckResultAdmin(admin.ModelAdmin):
    list_filter = ('forwarded', 'mirror',)
    search_fields = ('=hostname', '=port', 'country',)
    list_display = (
        'proxy', 'forwarded', 'ip_reveal', 'hostname', 'real_ip_address',
        'check_start', 'check_end', 'response_start', 'response_end',
        'mirror', 'id',)
    list_per_page = 25
    ordering = ('-id',)

    def has_add_permission(self, request, obj=None):
        return False

    def __init__(self, model, admin_site):
        admin.ModelAdmin.__init__(self, model, admin_site)
        self.readonly_fields = [field.name for field in model._meta.fields]
        self.readonly_model = model


class MirrorAdmin(admin.ModelAdmin):
    list_display = ('url', 'output_type', 'id',)
    list_filter = ('output_type',)
    search_fields = ('url',)
    list_per_page = 25


admin.site.register(Mirror, MirrorAdmin)
admin.site.register(Proxy, ProxyAdmin)

if settings.DEBUG:
    admin.site.register(ProxyCheckResult, ProxyCheckResultAdmin)
