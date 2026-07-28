from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PetRequest, Notification


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']


class PetRequestForm(forms.ModelForm):
    class Meta:
        model  = PetRequest
        fields = [
            'request_type', 'pet_name', 'pet_type', 'breed',
            'color', 'location', 'description', 'contact_number', 'pet_image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class AdminStatusForm(forms.ModelForm):
    """Admin updates status + optional note."""
    class Meta:
        model   = PetRequest
        fields  = ['status', 'admin_note']
        widgets = {
            'admin_note': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Optional: explain your decision to the user…',
            }),
        }


class PetSearchForm(forms.Form):
    """Public search form for lost pet inquiry."""
    q         = forms.CharField(
        required=False,
        label='Pet Name / Keyword',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Buddy, Golden Labrador, Banjara Hills…',
            'autocomplete': 'off',
        })
    )
    pet_type  = forms.ChoiceField(
        required=False,
        label='Pet Type',
        choices=[('', 'All Types')] + PetRequest.PET_TYPE_CHOICES,
    )
    location  = forms.CharField(
        required=False,
        label='Location',
        widget=forms.TextInput(attrs={'placeholder': 'City, area, landmark…'}),
    )
    req_type  = forms.ChoiceField(
        required=False,
        label='Report Type',
        choices=[('', 'Lost & Found'), ('LOST', 'Lost Only'), ('FOUND', 'Found Only')],
    )


class AdminNotificationForm(forms.ModelForm):
    """Admin manually sends a notification to a user."""
    class Meta:
        model   = Notification
        fields  = ['user', 'pet', 'notif_type', 'title', 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter your message to the user…',
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Your report has been reviewed',
            }),
        }
        labels = {
            'user':       'Send To (User)',
            'pet':        'Related Report (optional)',
            'notif_type': 'Notification Type',
            'title':      'Subject / Title',
            'message':    'Message',
        }
