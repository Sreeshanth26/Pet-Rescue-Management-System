# 🐾 Pet Rescue Management System

A full-stack Django web application for reporting, tracking, and managing lost and found pets with user authentication, notifications, profile management, admin dashboard, and responsive UI.

---

## ⚡ Quick Start (Windows PowerShell)

```powershell
# 1. Enter project folder
cd petrescue

# 2. Create & activate virtual environment
python -m venv venv
venv\Scripts\Activate.ps1
# If blocked: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Create admin superuser
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

---

## 📋 Pages

| URL | Description | Access |
|-----|-------------|--------|
| `/` | Browse accepted listings | Public |
| `/register/` | Create account | Public |
| `/login/` | Sign in | Public |
| `/create/` | Submit pet report | Logged in |
| `/myrequests/` | View & manage your reports | Logged in |
| `/edit/<id>/` | Edit pending report | Owner only |
| `/delete/<id>/` | Delete pending report | Owner only |
| `/admin-panel/` | Custom admin dashboard | Staff only |
| `/admin-panel/<id>/status/` | Review & update report | Staff only |
| `/django-admin/` | Django built-in admin | Superuser |

---

## 🔌 REST API

| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET | `/api/pets/` | List accepted pets | Public |
| GET | `/api/pets/?type=LOST&q=labrador` | Filter & search | Public |
| POST | `/api/pets/create/` | Submit new report | Login required |
| GET | `/api/pets/<pk>/` | Single pet detail | Public |
| PATCH | `/api/pets/<pk>/status/` | Update status | Staff only |

**PATCH example:**
```json
{"status": "ACCEPTED", "admin_note": "Verified and approved."}
```

---

## ✅ Milestone Coverage

**Milestone 1 — User Management**
- User registration, login, logout
- Session-based authentication
- PetRequest model with all required fields

**Milestone 2 — Pet Registration & Admin Management**
- Users raise Lost/Found requests with full pet details
- Custom Admin Panel to Accept / Reject reports
- Admin note displayed to the user
- Edit & delete own pending reports
- REST APIs for all operations
- Search, filter, pagination
