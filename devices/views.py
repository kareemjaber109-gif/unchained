from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import DeviceForm, ProjectForm
from .models import Device, Project


def _get_active_project(request):
    pid = request.session.get("active_project_id")
    if not pid:
        return None
    return Project.objects.filter(pk=pid, owner=request.user).first()


class ProjectRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not _get_active_project(request):
            first = Project.objects.filter(owner=request.user).order_by("-created_at").first()
            if first:
                request.session["active_project_id"] = first.pk
            else:
                messages.warning(request, "Create a project first to start adding devices.")
                return redirect(reverse("project-list"))
        return super().dispatch(request, *args, **kwargs)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "devices/project_list.html"
    context_object_name = "projects"
    login_url = "/accounts/login/"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_project"] = _get_active_project(self.request)
        return ctx


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "devices/project_form.html"
    success_url = reverse_lazy("project-list")
    login_url = "/accounts/login/"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["owner"] = self.request.user
        return kw

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        self.request.session["active_project_id"] = self.object.pk
        messages.success(self.request, f'Project "{self.object.name}" created and activated.')
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "create"
        return ctx


class ProjectEditView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "devices/project_form.html"
    success_url = reverse_lazy("project-list")
    login_url = "/accounts/login/"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["owner"] = self.request.user
        return kw

    def form_valid(self, form):
        messages.success(self.request, f'Project "{self.object.name}" updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "edit"
        return ctx


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "devices/project_confirm_delete.html"
    success_url = reverse_lazy("project-list")
    login_url = "/accounts/login/"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        name = str(self.object)
        was_active = request.session.get("active_project_id") == self.object.pk
        response = super().delete(request, *args, **kwargs)
        if was_active:
            first = Project.objects.filter(owner=request.user).order_by("-created_at").first()
            request.session["active_project_id"] = first.pk if first else None
        messages.success(request, f'Project "{name}" deleted.')
        return response


class ProjectSwitchView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def post(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        request.session["active_project_id"] = project.pk
        messages.success(request, f'Switched to project "{project.name}".')
        nxt = request.POST.get("next") or request.GET.get("next") or reverse("device-list")
        return redirect(nxt)

    def get(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        request.session["active_project_id"] = project.pk
        messages.success(request, f'Switched to project "{project.name}".')
        return redirect(reverse("device-list"))


class DeviceListView(ProjectRequiredMixin, ListView):
    model = Device
    template_name = "devices/device_list.html"
    context_object_name = "devices"
    login_url = "/accounts/login/"

    def get_queryset(self):
        project = _get_active_project(self.request)
        qs = Device.objects.filter(project=project)
        q = self.request.GET.get("q", "").strip()
        return qs.filter(name__icontains=q) if q else qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["active_project"] = _get_active_project(self.request)
        return ctx


class _MessageMixin:
    success_url = reverse_lazy("device-list")
    success_message = ""

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class DeviceCreateView(ProjectRequiredMixin, _MessageMixin, CreateView):
    model = Device
    form_class = DeviceForm
    template_name = "devices/device_form.html"
    success_message = "Device added successfully."
    login_url = "/accounts/login/"

    def form_valid(self, form):
        form.instance.project = _get_active_project(self.request)
        return super().form_valid(form)


class DeviceUpdateView(ProjectRequiredMixin, _MessageMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = "devices/device_form.html"
    success_message = "Device updated successfully."
    login_url = "/accounts/login/"

    def get_queryset(self):
        project = _get_active_project(self.request)
        return Device.objects.filter(project=project)


class DeviceDeleteView(ProjectRequiredMixin, DeleteView):
    model = Device
    template_name = "devices/device_confirm_delete.html"
    success_url = reverse_lazy("device-list")
    login_url = "/accounts/login/"

    def get_queryset(self):
        project = _get_active_project(self.request)
        return Device.objects.filter(project=project)

    def form_valid(self, form):
        messages.success(self.request, "Device deleted.")
        return super().form_valid(form)
