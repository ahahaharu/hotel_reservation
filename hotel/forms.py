from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Room, RoomCategory, RoomImage, Client

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'category', 'status', 'capacity', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class RoomImageForm(forms.ModelForm):
    class Meta:
        model = RoomImage
        fields = ['image', 'caption']

class RoomFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=RoomCategory.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        label="Minimum Price"
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        label="Maximum Price"
    )
    capacity = forms.IntegerField(
        required=False,
        min_value=1,
        label="Minimum Capacity"
    )
    available_only = forms.BooleanField(
        required=False,
        initial=True,
        label="Show only available rooms"
    )

