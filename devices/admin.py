from django.contrib import admin

from .models import Device, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at", "device_count")
    list_filter = ("created_at",)
    search_fields = ("name", "owner__username")

    def device_count(self, obj):
        return obj.devices.count()
    device_count.short_description = "Devices"


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "ip_address", "device_type", "vlan_id", "is_active")
    list_filter = ("device_type", "is_active", "project", "vlan_id")
    search_fields = ("name", "ip_address", "project__name")
