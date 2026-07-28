from django.contrib import admin
from django.utils.html import format_html
from .models import PetRequest, Notification


@admin.register(PetRequest)
class PetRequestAdmin(admin.ModelAdmin):
    list_display    = ('pet_name', 'pet_type', 'request_type', 'colored_status',
                       'location', 'created_by', 'created_at')
    list_filter     = ('status', 'request_type', 'pet_type')
    search_fields   = ('pet_name', 'location', 'breed', 'created_by__username')
    ordering        = ('-created_at',)
    list_per_page   = 20
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    actions         = ['accept_requests', 'reject_requests', 'reset_pending']

    fieldsets = (
        ('Pet Details', {
            'fields': ('pet_name', 'pet_type', 'breed', 'color', 'pet_image', 'description')
        }),
        ('Report Info', {
            'fields': ('request_type', 'location', 'contact_number')
        }),
        ('Admin Decision', {
            'fields': ('status', 'admin_note')
        }),
        ('Meta', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Status')
    def colored_status(self, obj):
        colors = {
            'PENDING':  ('#d97706', '⏳'),
            'ACCEPTED': ('#059669', '✅'),
            'REJECTED': ('#dc2626', '❌'),
        }
        color, icon = colors.get(obj.status, ('#6b7280', '•'))
        return format_html(
            '<span style="color:{};font-weight:700">{} {}</span>',
            color, icon, obj.get_status_display()
        )

    @admin.action(description='✅ Accept selected requests')
    def accept_requests(self, request, queryset):
        n = queryset.update(status='ACCEPTED')
        self.message_user(request, f'{n} request(s) accepted.')

    @admin.action(description='❌ Reject selected requests')
    def reject_requests(self, request, queryset):
        n = queryset.update(status='REJECTED')
        self.message_user(request, f'{n} request(s) rejected.')

    @admin.action(description='⏳ Reset selected to Pending')
    def reset_pending(self, request, queryset):
        n = queryset.update(status='PENDING')
        self.message_user(request, f'{n} request(s) reset to pending.')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('title', 'user', 'notif_type', 'is_read', 'created_at')
    list_filter   = ('notif_type', 'is_read')
    search_fields = ('title', 'message', 'user__username')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at',)
