# Django Network Device Inventory

Simple CRUD app to manage network devices (routers / switches).
Stack: Django 5+, SQLite, Django Templates, Bootstrap 5 (CDN).

## Features
- Device list table (name, IP, type, status) with search by name
- Add / Edit / Delete (with confirmation page)
- Django Admin (`/admin/`) with filters and search

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # for /admin/
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Tests
```bash
python manage.py test
```

## Structure
```
netinventory/
├── manage.py
├── requirements.txt
├── config/              # settings, root urls
└── devices/
    ├── models.py        # Device model
    ├── forms.py         # ModelForm + Bootstrap widgets
    ├── views.py         # Class-based CRUD views
    ├── urls.py
    ├── admin.py
    ├── tests.py
    └── templates/devices/
        ├── base.html
        ├── device_list.html
        ├── device_form.html
        └── device_confirm_delete.html
```
