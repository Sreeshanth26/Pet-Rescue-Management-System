from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json

from .forms import (RegisterForm, PetRequestForm, AdminStatusForm,
                    PetSearchForm, AdminNotificationForm)
from .models import PetRequest, Notification


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

def _send_notification(user, title, message, notif_type='MESSAGE', pet=None):
    """Helper: create a Notification record for a user."""
    Notification.objects.create(
        user=user, title=title, message=message,
        notif_type=notif_type, pet=pet,
    )


def _pet_to_dict(p):
    return {
        'id':             p.pk,
        'request_type':   p.request_type,
        'pet_name':       p.pet_name,
        'pet_type':       p.pet_type,
        'breed':          p.breed,
        'color':          p.color,
        'location':       p.location,
        'description':    p.description,
        'contact_number': p.contact_number,
        'status':         p.status,
        'admin_note':     p.admin_note,
        'pet_image':      p.pet_image.url if p.pet_image else None,
        'created_by':     p.created_by.username,
        'created_at':     p.created_at.isoformat(),
        'updated_at':     p.updated_at.isoformat(),
    }


# ─────────────────────────────────────────────────────────────
#  PUBLIC
# ─────────────────────────────────────────────────────────────

def home(request):
    qs = PetRequest.objects.filter(status='ACCEPTED').order_by('-created_at')

    rtype = request.GET.get('type', '')
    if rtype in ('LOST', 'FOUND'):
        qs = qs.filter(request_type=rtype)

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(pet_name__icontains=q) | Q(breed__icontains=q) |
            Q(location__icontains=q) | Q(pet_type__icontains=q) |
            Q(color__icontains=q)
        )

    paginator = Paginator(qs, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'pets/home.html', {
        'page_obj':    page_obj,
        'total':       PetRequest.objects.filter(status='ACCEPTED').count(),
        'filter_type': rtype,
        'query':       q,
    })


# ──────────────────────────────────────────────────────────────
#  PET STATUS INQUIRY / SEARCH  (Weeks 5-6)
# ──────────────────────────────────────────────────────────────

def pet_search(request):
    """
    Public search page — users check if their lost pet has been reported.
    Searches across ALL accepted requests (both LOST and FOUND reports).
    """
    form    = PetSearchForm(request.GET or None)
    results = None
    searched = False

    if request.GET and form.is_valid():
        searched = True
        qs = PetRequest.objects.filter(status='ACCEPTED').select_related('created_by')

        q        = form.cleaned_data.get('q', '').strip()
        pet_type = form.cleaned_data.get('pet_type', '')
        location = form.cleaned_data.get('location', '').strip()
        req_type = form.cleaned_data.get('req_type', '')

        if q:
            qs = qs.filter(
                Q(pet_name__icontains=q)    |
                Q(breed__icontains=q)       |
                Q(description__icontains=q) |
                Q(color__icontains=q)
            )
        if pet_type:
            qs = qs.filter(pet_type=pet_type)
        if location:
            qs = qs.filter(location__icontains=location)
        if req_type in ('LOST', 'FOUND'):
            qs = qs.filter(request_type=req_type)

        results = qs.order_by('-created_at')

    return render(request, 'pets/pet_search.html', {
        'form':     form,
        'results':  results,
        'searched': searched,
    })


# ─────────────────────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to PetRescue, {user.username}! 🐾')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'pets/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            return render(request, 'pets/login.html',
                          {'error': 'Please enter both username and password.'})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome back, {user.username}! 👋')
                nxt = request.GET.get('next', '')
                return redirect(nxt if nxt else 'home')
            return render(request, 'pets/login.html',
                          {'error': 'Your account is disabled.',
                           'username_entered': username})
        else:
            from django.contrib.auth.models import User as AU
            try:
                AU.objects.get(username=username)
                err = 'Incorrect password. Please try again.'
            except AU.DoesNotExist:
                err = f'No account found for "{username}". Did you mean to register?'
            return render(request, 'pets/login.html',
                          {'error': err, 'username_entered': username})
    return render(request, 'pets/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out. See you soon! 👋")
    return redirect('home')


# ─────────────────────────────────────────────────────────────
#  USER — PET REQUESTS
# ─────────────────────────────────────────────────────────────

@login_required
def create_request(request):
    if request.method == 'POST':
        form = PetRequestForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request,
                'Report submitted! It will appear publicly once an admin approves it. ✅')
            return redirect('my_requests')
    else:
        form = PetRequestForm()
    return render(request, 'pets/create_request.html', {'form': form, 'edit_mode': False})


@login_required
def edit_request(request, pk):
    pet = get_object_or_404(PetRequest, pk=pk, created_by=request.user)
    if pet.status != 'PENDING':
        messages.error(request, 'Only pending reports can be edited.')
        return redirect('my_requests')
    if request.method == 'POST':
        form = PetRequestForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Report updated. ✅')
            return redirect('my_requests')
    else:
        form = PetRequestForm(instance=pet)
    return render(request, 'pets/create_request.html',
                  {'form': form, 'edit_mode': True, 'pet': pet})


@login_required
def delete_request(request, pk):
    pet = get_object_or_404(PetRequest, pk=pk, created_by=request.user)
    if pet.status != 'PENDING':
        messages.error(request, 'Only pending reports can be deleted.')
        return redirect('my_requests')
    if request.method == 'POST':
        pet.delete()
        messages.success(request, 'Report deleted.')
    return redirect('my_requests')


@login_required
def my_requests(request):
    pets = PetRequest.objects.filter(created_by=request.user).order_by('-created_at')
    counts = {
        'total':    pets.count(),
        'pending':  pets.filter(status='PENDING').count(),
        'accepted': pets.filter(status='ACCEPTED').count(),
        'rejected': pets.filter(status='REJECTED').count(),
    }
    return render(request, 'pets/my_requests.html', {'pets': pets, 'counts': counts})


# ─────────────────────────────────────────────────────────────
#  NOTIFICATIONS  (Weeks 5-6)
# ─────────────────────────────────────────────────────────────

@login_required
def my_notifications(request):
    """User views all their notifications."""
    notifs = Notification.objects.filter(
        user=request.user).select_related('pet').order_by('-created_at')

    # Mark all as read on visit
    notifs.filter(is_read=False).update(is_read=True)

    unread_count = 0   # already marked read above
    return render(request, 'pets/notifications.html', {
        'notifs':       notifs,
        'unread_count': unread_count,
    })


@login_required
def mark_notification_read(request, pk):
    """Mark a single notification as read (AJAX or direct)."""
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('my_notifications')


# ─────────────────────────────────────────────────────────────
#  ADMIN PANEL  (staff only)
# ─────────────────────────────────────────────────────────────

@staff_member_required
def admin_dashboard(request):
    status_filter = request.GET.get('status', 'PENDING')
    type_filter   = request.GET.get('type',   '')
    q             = request.GET.get('q',      '').strip()

    qs = PetRequest.objects.select_related('created_by').all()

    if status_filter:
        qs = qs.filter(status=status_filter)
    if type_filter in ('LOST', 'FOUND'):
        qs = qs.filter(request_type=type_filter)
    if q:
        qs = qs.filter(
            Q(pet_name__icontains=q) | Q(location__icontains=q) |
            Q(created_by__username__icontains=q)
        )

    paginator = Paginator(qs.order_by('-created_at'), 15)
    page_obj  = paginator.get_page(request.GET.get('page'))

    counts = {
        'all':      PetRequest.objects.count(),
        'pending':  PetRequest.objects.filter(status='PENDING').count(),
        'accepted': PetRequest.objects.filter(status='ACCEPTED').count(),
        'rejected': PetRequest.objects.filter(status='REJECTED').count(),
    }

    return render(request, 'pets/admin_dashboard.html', {
        'page_obj':      page_obj,
        'counts':        counts,
        'status_filter': status_filter,
        'type_filter':   type_filter,
        'query':         q,
    })


@staff_member_required
def admin_update_status(request, pk):
    """Review a report and update its status. Auto-sends notification to user."""
    pet = get_object_or_404(PetRequest, pk=pk)

    if request.method == 'POST':
        old_status = pet.status
        form = AdminStatusForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            new_status = pet.status

            # ── Auto-notify user when status changes ──────────────────────
            if new_status != old_status:
                if new_status == 'ACCEPTED':
                    _send_notification(
                        user=pet.created_by,
                        title=f'Your report for "{pet.pet_name}" has been accepted!',
                        message=(
                            f'Great news! Your {pet.request_type.lower()} pet report for '
                            f'"{pet.pet_name}" has been reviewed and accepted by our admin. '
                            f'It is now visible publicly on PetRescue.'
                            + (f'\n\nAdmin note: {pet.admin_note}' if pet.admin_note else '')
                        ),
                        notif_type='ACCEPTED',
                        pet=pet,
                    )
                elif new_status == 'REJECTED':
                    _send_notification(
                        user=pet.created_by,
                        title=f'Your report for "{pet.pet_name}" was not approved',
                        message=(
                            f'Unfortunately your {pet.request_type.lower()} pet report for '
                            f'"{pet.pet_name}" could not be approved at this time.'
                            + (f'\n\nReason: {pet.admin_note}' if pet.admin_note else
                               '\n\nPlease contact us if you have questions.')
                        ),
                        notif_type='REJECTED',
                        pet=pet,
                    )

            messages.success(request,
                f'"{pet.pet_name}" updated to {pet.get_status_display()}. '
                f'{"Notification sent to user." if new_status != old_status else ""}')
            return redirect(f'{request.path}?updated=1')
    else:
        form = AdminStatusForm(instance=pet)

    return render(request, 'pets/admin_pet_detail.html', {
        'pet':  pet,
        'form': form,
        'updated': request.GET.get('updated') == '1',
    })


@staff_member_required
def admin_send_notification(request):
    """Admin manually sends a notification to any user."""
    if request.method == 'POST':
        form = AdminNotificationForm(request.POST)
        if form.is_valid():
            notif = form.save()
            messages.success(request,
                f'Notification sent to {notif.user.username} successfully. ✅')
            return redirect('admin_send_notification')
    else:
        # Pre-fill user/pet from query params (from dashboard quick-send)
        initial = {}
        if request.GET.get('user'):
            initial['user'] = request.GET.get('user')
        if request.GET.get('pet'):
            initial['pet'] = request.GET.get('pet')
        form = AdminNotificationForm(initial=initial)

    # Recent notifications sent
    recent = Notification.objects.select_related(
        'user', 'pet').order_by('-created_at')[:20]

    return render(request, 'pets/admin_send_notification.html', {
        'form':   form,
        'recent': recent,
    })


# ─────────────────────────────────────────────────────────────
#  REST API
# ─────────────────────────────────────────────────────────────

@require_http_methods(['GET'])
def api_pet_list(request):
    """GET /api/pets/ — list ACCEPTED pet requests. Public."""
    qs = PetRequest.objects.filter(status='ACCEPTED').select_related('created_by')
    rtype = request.GET.get('type', '').upper()
    if rtype in ('LOST', 'FOUND'):
        qs = qs.filter(request_type=rtype)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(pet_name__icontains=q) | Q(location__icontains=q) |
            Q(breed__icontains=q)    | Q(pet_type__icontains=q)
        )
    return JsonResponse({'count': qs.count(), 'results': [_pet_to_dict(p) for p in qs]})


@login_required
@require_http_methods(['POST'])
def api_create_pet(request):
    """POST /api/pets/create/ — submit new report. Auth required."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    form = PetRequestForm(data)
    if form.is_valid():
        pet = form.save(commit=False)
        pet.created_by = request.user
        pet.save()
        return JsonResponse({'success': True, 'pet': _pet_to_dict(pet)}, status=201)
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_http_methods(['GET'])
def api_pet_detail(request, pk):
    """GET /api/pets/<pk>/ — single pet detail."""
    pet = get_object_or_404(PetRequest, pk=pk)
    if pet.status != 'ACCEPTED' and not request.user.is_staff:
        return JsonResponse({'error': 'Not found.'}, status=404)
    return JsonResponse(_pet_to_dict(pet))


@staff_member_required
@require_http_methods(['PATCH', 'POST'])
def api_update_status(request, pk):
    """PATCH /api/pets/<pk>/status/ — update status. Staff only."""
    pet = get_object_or_404(PetRequest, pk=pk)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    new_status = data.get('status', '').upper()
    valid = [s[0] for s in PetRequest.STATUS_TYPE]
    if new_status not in valid:
        return JsonResponse({'error': f'Invalid status. Valid: {valid}'}, status=400)

    old_status     = pet.status
    pet.status     = new_status
    pet.admin_note = data.get('admin_note', pet.admin_note)
    pet.save(update_fields=['status', 'admin_note', 'updated_at'])

    # Auto-notify via API too
    if new_status != old_status:
        if new_status == 'ACCEPTED':
            _send_notification(
                user=pet.created_by,
                title=f'Your report for "{pet.pet_name}" has been accepted!',
                message=f'Your report is now live on PetRescue.'
                        + (f' Note: {pet.admin_note}' if pet.admin_note else ''),
                notif_type='ACCEPTED', pet=pet,
            )
        elif new_status == 'REJECTED':
            _send_notification(
                user=pet.created_by,
                title=f'Your report for "{pet.pet_name}" was not approved',
                message=f'Your report could not be approved.'
                        + (f' Reason: {pet.admin_note}' if pet.admin_note else ''),
                notif_type='REJECTED', pet=pet,
            )

    return JsonResponse({'success': True, 'pet': _pet_to_dict(pet)})


@login_required
@require_http_methods(['GET'])
def api_my_notifications(request):
    """GET /api/notifications/ — current user's notifications."""
    notifs = Notification.objects.filter(user=request.user).select_related('pet')
    data = [{
        'id':         n.pk,
        'type':       n.notif_type,
        'title':      n.title,
        'message':    n.message,
        'is_read':    n.is_read,
        'pet_id':     n.pet.pk if n.pet else None,
        'created_at': n.created_at.isoformat(),
    } for n in notifs]
    return JsonResponse({'count': len(data), 'results': data})
