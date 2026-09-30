from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import DeviceForm
from .models import Device


class DeviceListView(ListView):
    model = Device
    template_name = "devices/device_list.html"
    context_object_name = "devices"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        return qs.filter(name__icontains=q) if q else qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class _MessageMixin:
    success_url = reverse_lazy("device-list")
    success_message = ""

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class DeviceCreateView(_MessageMixin, CreateView):
    model = Device
    form_class = DeviceForm
    template_name = "devices/device_form.html"
    success_message = "Device added successfully."


class DeviceUpdateView(_MessageMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = "devices/device_form.html"
    success_message = "Device updated successfully."


class DeviceDeleteView(DeleteView):
    model = Device
    template_name = "devices/device_confirm_delete.html"
    success_url = reverse_lazy("device-list")

    def form_valid(self, form):
        messages.success(self.request, "Device deleted.")
        return super().form_valid(form)
