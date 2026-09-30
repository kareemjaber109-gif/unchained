from django.db import models


class Device(models.Model):
    class DeviceType(models.TextChoices):
        ROUTER = "router", "Router"
        SWITCH = "switch", "Switch"

    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(unique=True)
    device_type = models.CharField(max_length=10, choices=DeviceType.choices, default=DeviceType.ROUTER)
    is_active = models.BooleanField("Active", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.ip_address})"
