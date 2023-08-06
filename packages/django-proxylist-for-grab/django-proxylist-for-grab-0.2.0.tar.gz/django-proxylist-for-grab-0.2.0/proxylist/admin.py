# -*- coding: utf-8 -*-

from django.contrib import admin

from proxylist.models import Proxy, Mirror, ProxyCheckResult


class ProxyAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'port', 'country', 'anonymity_level',
                    'last_check', 'proxy_type', 'errors',)
    list_filter = ('anonymity_level', 'proxy_type', 'country',)
    search_fields = ('=hostname', '=port', 'country',)
    list_per_page = 25


class ProxyCheckResultAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def __init__(self, model, admin_site):
        admin.ModelAdmin.__init__(self, model, admin_site)
        self.readonly_fields = [field.name for field in model._meta.fields]
        self.readonly_model = model


admin.site.register(Mirror)
admin.site.register(Proxy, ProxyAdmin)
admin.site.register(ProxyCheckResult, ProxyCheckResultAdmin)
