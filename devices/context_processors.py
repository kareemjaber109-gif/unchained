from .models import Project


def projects_navbar(request):
    if not request.user.is_authenticated:
        return {}
    projects = Project.objects.filter(owner=request.user).order_by("-created_at")
    active_pid = request.session.get("active_project_id")
    active = None
    if active_pid:
        active = next((p for p in projects if p.pk == active_pid), None)
    return {
        "all_projects": projects,
        "active_project": active,
    }
