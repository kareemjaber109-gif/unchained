from django.urls import path

from . import views

urlpatterns = [
    path("projects/", views.ProjectListView.as_view(), name="project-list"),
    path("projects/add/", views.ProjectCreateView.as_view(), name="project-add"),
    path("projects/<int:pk>/edit/", views.ProjectEditView.as_view(), name="project-edit"),
    path("projects/<int:pk>/delete/", views.ProjectDeleteView.as_view(), name="project-delete"),
    path("projects/<int:pk>/switch/", views.ProjectSwitchView.as_view(), name="project-switch"),

    path("", views.DeviceListView.as_view(), name="device-list"),
    path("add/", views.DeviceCreateView.as_view(), name="device-add"),
    path("<int:pk>/edit/", views.DeviceUpdateView.as_view(), name="device-edit"),
    path("<int:pk>/delete/", views.DeviceDeleteView.as_view(), name="device-delete"),
]
