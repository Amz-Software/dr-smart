from django.contrib import admin
from django.contrib.auth.models import Permission

class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type')

admin.site.register(Permission, PermissionAdmin)