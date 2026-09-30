from django.test import TestCase
from django.urls import reverse

from .models import Device


class DeviceCRUDTests(TestCase):
    def setUp(self):
        self.d = Device.objects.create(name="Core-R1", ip_address="10.0.0.1", device_type="router")

    def test_list_and_search(self):
        Device.objects.create(name="Access-SW1", ip_address="10.0.0.2", device_type="switch")
        r = self.client.get(reverse("device-list"), {"q": "core"})
        self.assertContains(r, "Core-R1")
        self.assertNotContains(r, "Access-SW1")

    def test_create(self):
        r = self.client.post(reverse("device-add"), {"name": "SW2", "ip_address": "10.0.0.3", "device_type": "switch", "is_active": "on"})
        self.assertRedirects(r, reverse("device-list"))
        self.assertTrue(Device.objects.filter(name="SW2", is_active=True).exists())

    def test_update(self):
        self.client.post(reverse("device-edit", args=[self.d.pk]), {"name": "Core-R1b", "ip_address": "10.0.0.1", "device_type": "router"})
        self.d.refresh_from_db()
        self.assertEqual(self.d.name, "Core-R1b")
        self.assertFalse(self.d.is_active)

    def test_delete(self):
        self.client.post(reverse("device-delete", args=[self.d.pk]))
        self.assertFalse(Device.objects.exists())
