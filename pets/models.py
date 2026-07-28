from django.db import models
from django.contrib.auth.models import User


class PetRequest(models.Model):

    REQUEST_TYPE = [
        ('LOST',  'Lost'),
        ('FOUND', 'Found'),
    ]

    STATUS_TYPE = [
        ('PENDING',  'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    PET_TYPE_CHOICES = [
        ('Dog',    'Dog'),
        ('Cat',    'Cat'),
        ('Bird',   'Bird'),
        ('Rabbit', 'Rabbit'),
        ('Other',  'Other'),
    ]

    request_type   = models.CharField(max_length=10,  choices=REQUEST_TYPE)
    pet_name       = models.CharField(max_length=100)
    pet_type       = models.CharField(max_length=50,  choices=PET_TYPE_CHOICES)
    breed          = models.CharField(max_length=100, blank=True)
    color          = models.CharField(max_length=50)
    location       = models.CharField(max_length=200)
    description    = models.TextField()
    contact_number = models.CharField(max_length=15)
    pet_image      = models.ImageField(upload_to='pet_images/', null=True, blank=True)

    status         = models.CharField(max_length=10, choices=STATUS_TYPE, default='PENDING')
    admin_note     = models.TextField(blank=True,
                        help_text='Optional note shown to the user about this decision')

    created_by     = models.ForeignKey(User, on_delete=models.CASCADE,
                                       related_name='pet_requests')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.pet_name} ({self.request_type}) — {self.status}"


class Notification(models.Model):
    """In-app notification sent to a user by the admin."""

    NOTIF_TYPE = [
        ('ACCEPTED',  'Report Accepted'),
        ('REJECTED',  'Report Rejected'),
        ('MATCH',     'Possible Match Found'),
        ('MESSAGE',   'Message from Admin'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='notifications')
    pet        = models.ForeignKey(PetRequest, on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='notifications')
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE,
                                  default='MESSAGE')
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type}] → {self.user.username}: {self.title}"
