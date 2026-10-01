from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Device, Project


class ProjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")
        self.client.login(username="testuser", password="TestPass123!")

    def test_project_list_empty(self):
        r = self.client.get(reverse("project-list"))
        self.assertContains(r, "No projects yet")
        self.assertContains(r, "Create Your First Project")

    def test_project_create(self):
        r = self.client.post(reverse("project-add"), {"name": "Lab 1", "description": "Test project"})
        self.assertRedirects(r, reverse("project-list"))
        p = Project.objects.get(name="Lab 1")
        self.assertEqual(p.owner, self.user)
        self.assertEqual(self.client.session.get("active_project_id"), p.pk)

    def test_project_unique_per_user(self):
        Project.objects.create(name="Dup", owner=self.user)
        r = self.client.post(reverse("project-add"), {"name": "Dup", "description": "x"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Project.objects.filter(name="Dup", owner=self.user).count(), 1)

    def test_project_switch_and_scoping(self):
        p1 = Project.objects.create(name="P1", owner=self.user)
        p2 = Project.objects.create(name="P2", owner=self.user)
        r = self.client.post(reverse("project-switch", args=[p2.pk]))
        self.assertRedirects(r, reverse("device-list"))
        self.assertEqual(self.client.session.get("active_project_id"), p2.pk)

    def test_other_user_project_inaccessible(self):
        other = User.objects.create_user(username="other", password="TestPass123!")
        p = Project.objects.create(name="Hidden", owner=other)
        r = self.client.get(reverse("project-edit", args=[p.pk]))
        self.assertEqual(r.status_code, 404)

    def test_project_delete_cascades(self):
        p = Project.objects.create(name="Gone", owner=self.user)
        Device.objects.create(name="D1", ip_address="10.0.0.1", device_type="router", project=p)
        self.client.post(reverse("project-delete", args=[p.pk]))
        self.assertFalse(Project.objects.filter(pk=p.pk).exists())
        self.assertFalse(Device.objects.filter(name="D1").exists())


class DeviceCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")
        self.client.login(username="testuser", password="TestPass123!")
        self.project = Project.objects.create(name="Proj1", owner=self.user)
        session = self.client.session
        session["active_project_id"] = self.project.pk
        session.save()
        self.d = Device.objects.create(
            name="Core-R1", ip_address="10.0.0.1", device_type="router",
            project=self.project, vlan_id=10,
        )

    def test_no_project_redirects_to_project_list(self):
        Project.objects.filter(owner=self.user).delete()
        s = self.client.session
        del s["active_project_id"]
        s.save()
        r = self.client.get(reverse("device-list"), follow=False)
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("project-list"), r.url)

    def test_list_and_search(self):
        Device.objects.create(name="Access-SW1", ip_address="10.0.0.2", device_type="switch",
                              project=self.project, vlan_id=20)
        r = self.client.get(reverse("device-list"), {"q": "core"})
        self.assertContains(r, "Core-R1")
        self.assertContains(r, "10")
        self.assertNotContains(r, "Access-SW1")

    def test_devices_isolated_by_project(self):
        other = Project.objects.create(name="Other", owner=self.user)
        Device.objects.create(name="Lonely", ip_address="10.0.0.5", device_type="router", project=other)
        r = self.client.get(reverse("device-list"))
        self.assertContains(r, "Core-R1")
        self.assertNotContains(r, "Lonely")

    def test_vlan_id_in_list(self):
        r = self.client.get(reverse("device-list"))
        self.assertContains(r, "VLAN")
        self.assertContains(r, "10")

    def test_create_with_vlan(self):
        r = self.client.post(reverse("device-add"),
                             {"name": "SW2", "ip_address": "10.0.0.3", "device_type": "switch",
                              "vlan_id": 30, "is_active": "on"})
        self.assertRedirects(r, reverse("device-list"))
        dev = Device.objects.get(name="SW2")
        self.assertTrue(dev.is_active)
        self.assertEqual(dev.vlan_id, 30)
        self.assertEqual(dev.project, self.project)

    def test_create_without_vlan(self):
        r = self.client.post(reverse("device-add"),
                             {"name": "R2", "ip_address": "10.0.0.4", "device_type": "router", "is_active": "on"})
        self.assertRedirects(r, reverse("device-list"))
        dev = Device.objects.get(name="R2")
        self.assertIsNone(dev.vlan_id)

    def test_update_vlan(self):
        self.client.post(reverse("device-edit", args=[self.d.pk]),
                         {"name": "Core-R1b", "ip_address": "10.0.0.1",
                          "device_type": "router", "vlan_id": 99})
        self.d.refresh_from_db()
        self.assertEqual(self.d.name, "Core-R1b")
        self.assertEqual(self.d.vlan_id, 99)
        self.assertFalse(self.d.is_active)

    def test_vlan_valid_range(self):
        r_invalid_low = self.client.post(reverse("device-add"),
                                         {"name": "Bad1", "ip_address": "10.0.0.5", "device_type": "switch",
                                          "vlan_id": 0, "is_active": "on"})
        self.assertEqual(r_invalid_low.status_code, 200)
        self.assertFalse(Device.objects.filter(name="Bad1").exists())

        r_invalid_high = self.client.post(reverse("device-add"),
                                          {"name": "Bad2", "ip_address": "10.0.0.6", "device_type": "switch",
                                           "vlan_id": 4095, "is_active": "on"})
        self.assertEqual(r_invalid_high.status_code, 200)
        self.assertFalse(Device.objects.filter(name="Bad2").exists())

    def test_same_ip_different_projects_ok(self):
        other = Project.objects.create(name="P2", owner=self.user)
        Device.objects.create(name="DupIP", ip_address="10.0.0.1", device_type="switch", project=other)
        self.assertTrue(Device.objects.filter(ip_address="10.0.0.1").count(), 2)

    def test_delete(self):
        self.client.post(reverse("device-delete", args=[self.d.pk]))
        self.assertFalse(Device.objects.exists())

