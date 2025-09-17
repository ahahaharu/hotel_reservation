from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Room, RoomCategory, RoomImage, Client, Review

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
    
    search = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={'placeholder': 'Search room number or description'})
    )
    
    SORT_CHOICES = [
        ('room_number', 'Room Number (ascending)'),
        ('-room_number', 'Room Number (descending)'),
        ('category__base_price', 'Price (low to high)'),
        ('-category__base_price', 'Price (high to low)'),
        ('capacity', 'Capacity (low to high)'),
        ('-capacity', 'Capacity (high to low)'),
    ]
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='room_number',
        label="Sort by"
    )

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about your experience...'}),
            'rating': forms.Select(attrs={'class': 'form-control'})
        }