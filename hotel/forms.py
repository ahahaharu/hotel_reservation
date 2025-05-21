from django import forms
from .models import Room, RoomCategory, RoomImage

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