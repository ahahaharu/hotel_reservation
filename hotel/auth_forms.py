from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Client
from datetime import date, timedelta

class UserRegisterForm(UserCreationForm):
    """Extended user registration form with email field"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    phone = forms.CharField(
        max_length=20, 
        required=True,
        help_text="Format: +375 (29) XXX-XX-XX or (29) XXX-XX-XX"
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        help_text="Must be at least 18 years old"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'date_of_birth', 'password1', 'password2']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        return validate_and_format_phone(phone)
    
    def clean_date_of_birth(self):
        """Validate that the user is at least 18 years old"""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise ValidationError("You must be at least 18 years old to register.")
        return dob
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            client = Client(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone'],  
                date_of_birth=self.cleaned_data['date_of_birth'] 
            )
            client.save()
        
        return user
    
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            client = Client(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone'],
                date_of_birth=self.cleaned_data['date_of_birth'] 
            )
            client.save()
        
        return user

class UserLoginForm(AuthenticationForm):
    """Custom login form with custom styling"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class UserRegisterForm(UserCreationForm):
    """Extended user registration form with email field"""
    email = forms.EmailField(
        required=True,
        help_text="Enter a valid email address."
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        help_text="Enter your first name."
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        help_text="Enter your last name."
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        help_text="Format: +375 (29) XXX-XX-XX or (29) XXX-XX-XX"
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        help_text="Must be at least 18 years old."
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'date_of_birth', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        return validate_and_format_phone(phone)
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise ValidationError("You must be at least 18 years old to register.")
        return dob
    
def validate_and_format_phone(value):
    """Validate and format Belarusian phone number"""
    digits_only = re.sub(r'\D', '', value)
    
    if len(digits_only) != 12 and len(digits_only) != 9:
        raise ValidationError(
            'Phone number must be in format +375 (XX) XXX-XX-XX or (XX) XXX-XX-XX'
        )
    
    if len(digits_only) == 9: 
        formatted_number = f"+375 ({digits_only[0:2]}) {digits_only[2:5]}-{digits_only[5:7]}-{digits_only[7:9]}"
    else:  
        if not digits_only.startswith('375'):
            raise ValidationError('Belarusian phone number must start with 375')
        formatted_number = f"+{digits_only[0:3]} ({digits_only[3:5]}) {digits_only[5:8]}-{digits_only[8:10]}-{digits_only[10:12]}"
    
    return formatted_number

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile (Client model)"""
    phone = forms.CharField(
        max_length=20, 
        required=True,
        help_text="Format: +375 (29) XXX-XX-XX or (29) XXX-XX-XX"
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        help_text="Must be at least 18 years old"
    )
    
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'phone', 'address', 'date_of_birth']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        return validate_and_format_phone(phone)
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise ValidationError("You must be at least 18 years old.")
        return dob