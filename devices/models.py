from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "name"]
        unique_together = ("owner", "name")

    def __str__(self):
        return self.name


class Device(models.Model):
    class DeviceType(models.TextChoices):
        ROUTER = "router", "Router"
        SWITCH = "switch", "Switch"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="devices",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    device_type = models.CharField(max_length=10, choices=DeviceType.choices, default=DeviceType.ROUTER)
    vlan_id = models.PositiveIntegerField(
        "VLAN ID",
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(4094)],
    )
    is_active = models.BooleanField("Active", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("project", "ip_address")

    def __str__(self):
        return f"{self.name} ({self.ip_address})"
