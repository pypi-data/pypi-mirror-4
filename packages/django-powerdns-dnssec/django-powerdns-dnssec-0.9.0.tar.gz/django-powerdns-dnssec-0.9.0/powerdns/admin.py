# -*- coding: utf-8 -*-

from django.contrib import admin
from powerdns.models import (CryptoKey, Domain, DomainMetadata, Record,
                             SuperMaster)


class RecordAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'type', 'content', 'domain', 'ttl', 'prio', 'change_date',
    )
    list_filter = ('type', 'ttl', 'domain',)
    search_fields = ('name', 'content',)
    readonly_fields = ('change_date', 'ordername',)
    fieldsets = (
        (None, {
            'fields': ('domain', ('type', 'name', 'content',), 'auth',)
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('prio', 'ttl', 'ordername', 'change_date',)
        }),
    )


class DomainMetadataInline(admin.TabularInline):
    model = DomainMetadata
    extra = 0


class DomainAdmin(admin.ModelAdmin):
    inlines = [DomainMetadataInline]
    list_display = ('name', 'type', 'last_check', 'account',)
    list_filter = ('type', 'last_check', 'account',)
    search_fields = ('name',)
    readonly_fields = ('notified_serial',)


class SuperMasterAdmin(admin.ModelAdmin):
    list_display = ('ip', 'nameserver', 'account',)
    list_filter = ('ip', 'account',)
    search_fields = ('ip', 'nameserver',)


class DomainMetadataAdmin(admin.ModelAdmin):
    list_display = ('domain', 'kind', 'content',)
    list_filter = ('kind', 'domain',)
    search_fields = ('content',)


class CryptoKeyAdmin(admin.ModelAdmin):
    list_display = ('domain', 'flags', 'active', 'content',)
    list_filter = ('active', 'domain',)
    search_fields = ('content',)


admin.site.register(Domain, DomainAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(SuperMaster, SuperMasterAdmin)
admin.site.register(DomainMetadata, DomainMetadataAdmin)
admin.site.register(CryptoKey, CryptoKeyAdmin)
