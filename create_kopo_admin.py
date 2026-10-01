import os
import sys
import django

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

ADMIN_USERNAME = "kopo_admin"
ADMIN_PASSWORD = "Kopo!Secure2026"
ADMIN_EMAIL = "kopo@example.com"


def main():
    print("=" * 60)
    print("  kopo Admin User Setup")
    print("=" * 60)
    print()

    existing = User.objects.filter(username=ADMIN_USERNAME).first()
    if existing:
        print(f"[INFO] User '{ADMIN_USERNAME}' already exists.")
        if not existing.is_superuser:
            existing.is_superuser = True
            existing.is_staff = True
            existing.save()
            print(f"[UPDATED] Granted superuser/staff privileges to '{ADMIN_USERNAME}'.")
    else:
        try:
            User.objects.create_superuser(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD,
            )
            print(f"[CREATED] Superuser '{ADMIN_USERNAME}' created successfully.")
        except Exception as exc:
            print(f"[ERROR] Failed to create superuser: {exc}")
            sys.exit(1)

    old_admin = User.objects.filter(username="admin").first()
    if old_admin:
        print(f"[WARN] Legacy user 'admin' still exists in the database (id={old_admin.pk}).")

    print()
    print("=" * 60)
    print("  ADMIN CREDENTIALS (SAVE THESE!)")
    print("=" * 60)
    print(f"  Admin Panel URL : http://localhost:8000/kopo-manage/")
    print(f"  Username        : {ADMIN_USERNAME}")
    print(f"  Password        : {ADMIN_PASSWORD}")
    print(f"  Email           : {ADMIN_EMAIL}")
    print("=" * 60)


if __name__ == "__main__":
    main()
