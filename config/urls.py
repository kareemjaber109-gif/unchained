from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

admin.site.site_header = "kopo Administration"
admin.site.site_title = "kopo Admin Portal"
admin.site.index_title = "Welcome to kopo Management"

urlpatterns = [
    path("kopo-manage/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("devices.urls")),
]
