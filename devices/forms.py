from django import forms
from django.core.exceptions import ValidationError

from .models import Device, Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. CCNA Lab 1"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Short note about this project...", "rows": 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name or not self.owner:
            return name
        qs = Project.objects.filter(owner=self.owner, name=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("You already have a project with this name.")
        return name


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ["name", "ip_address", "device_type", "vlan_id", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Core-Router-01"}),
            "ip_address": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 192.168.1.1"}),
            "device_type": forms.Select(attrs={"class": "form-select"}),
            "vlan_id": forms.NumberInput(attrs={"class": "form-control", "placeholder": "1-4094 (optional)", "min": 1, "max": 4094}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
