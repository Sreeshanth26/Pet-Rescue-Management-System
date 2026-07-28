from django.urls import path
from . import views

urlpatterns = [

    # ── Public ──────────────────────────────────────────────────
    path('',          views.home,          name='home'),
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # ── Pet Status Inquiry / Search (Weeks 5-6) ─────────────────
    path('search/',   views.pet_search,    name='pet_search'),

    # ── Authenticated User ───────────────────────────────────────
    path('create/',          views.create_request,        name='create_request'),
    path('myrequests/',      views.my_requests,           name='my_requests'),
    path('edit/<int:pk>/',   views.edit_request,          name='edit_request'),
    path('delete/<int:pk>/', views.delete_request,        name='delete_request'),

    # ── Notifications (Weeks 5-6) ────────────────────────────────
    path('notifications/',                    views.my_notifications,       name='my_notifications'),
    path('notifications/<int:pk>/read/',      views.mark_notification_read, name='mark_notification_read'),

    # ── Admin Panel (staff only) ─────────────────────────────────
    path('admin-panel/',              views.admin_dashboard,         name='admin_dashboard'),
    path('admin-panel/<int:pk>/status/', views.admin_update_status,  name='admin_update_status'),
    path('admin-panel/notify/',       views.admin_send_notification, name='admin_send_notification'),

    # ── REST API ─────────────────────────────────────────────────
    path('api/pets/',                   views.api_pet_list,          name='api_pet_list'),
    path('api/pets/create/',            views.api_create_pet,        name='api_create_pet'),
    path('api/pets/<int:pk>/',          views.api_pet_detail,        name='api_pet_detail'),
    path('api/pets/<int:pk>/status/',   views.api_update_status,     name='api_update_status'),
    path('api/notifications/',          views.api_my_notifications,  name='api_my_notifications'),
]
