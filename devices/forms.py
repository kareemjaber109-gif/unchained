from django import forms

from .models import Device


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ["name", "ip_address", "device_type", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Core-Router-01"}),
            "ip_address": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 192.168.1.1"}),
            "device_type": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
