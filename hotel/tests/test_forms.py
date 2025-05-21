from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from hotel.forms import RoomForm, RoomFilterForm
from hotel.auth_forms import UserRegisterForm, UserLoginForm, validate_and_format_phone
from hotel.models import RoomCategory, Room
from django.core.exceptions import ValidationError

class RoomFormTest(TestCase):
    def setUp(self):
        self.category = RoomCategory.objects.create(
            name='Standard',
            description='Standard room',
            base_price=100.00
        )
        
    def test_room_form_valid(self):
        form_data = {
            'room_number': '101',
            'category': self.category.id,
            'status': 'available',
            'capacity': 2,
            'description': 'Nice room with a view'
        }
        form = RoomForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_room_form_invalid(self):
        # Test with missing required fields
        form_data = {
            'room_number': '',  # Empty room number
            'category': self.category.id,
            'status': 'available',
        }
        form = RoomForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('room_number', form.errors)

class RoomFilterFormTest(TestCase):
    def setUp(self):
        self.category = RoomCategory.objects.create(
            name='Standard',
            description='Standard room',
            base_price=100.00
        )
    
    def test_filter_form_valid(self):
        form_data = {
            'category': self.category.id,
            'min_price': 50,
            'max_price': 150,
            'capacity': 2,
            'available_only': True,
            'search': 'view',
            'sort_by': 'room_number'
        }
        form = RoomFilterForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_filter_form_empty(self):
        # All fields are optional, so empty form should be valid
        form = RoomFilterForm(data={})
        self.assertTrue(form.is_valid())

class UserRegisterFormTest(TestCase):
    def setUp(self):
        # Create a user that we'll use to test unique email constraint
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )
    
    def test_register_form_valid(self):
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+375 (29) 123-45-67',
            'date_of_birth': date(1990, 1, 1),
            'password1': 'complex_password123',
            'password2': 'complex_password123'
        }
        form = UserRegisterForm(data=form_data)
        
        if not form.is_valid():
            print(form.errors)  # For debugging
            
        self.assertTrue(form.is_valid())
    
    def test_register_form_email_already_exists(self):
        form_data = {
            'username': 'anotheruser',
            'email': 'existing@example.com',  # This email already exists
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '+375 (29) 123-45-67',
            'date_of_birth': date(1990, 1, 1),
            'password1': 'complex_password123',
            'password2': 'complex_password123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_register_form_underage(self):
        today = date.today()
        underage_date = date(today.year - 17, today.month, today.day)  # 17 years old
        
        form_data = {
            'username': 'younguser',
            'email': 'young@example.com',
            'first_name': 'Young',
            'last_name': 'User',
            'phone': '+375 (29) 123-45-67',
            'date_of_birth': underage_date,
            'password1': 'complex_password123',
            'password2': 'complex_password123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)

class PhoneValidationTest(TestCase):
    def test_valid_phone_formats(self):
        # Test valid phone formats
        test_cases = [
            ("+375291234567", "+375 (29) 123-45-67"),
            ("375291234567", "+375 (29) 123-45-67"),
            ("291234567", "+375 (29) 123-45-67"),
            ("+375 (29) 123-45-67", "+375 (29) 123-45-67"),
        ]
        
        for input_phone, expected_output in test_cases:
            self.assertEqual(validate_and_format_phone(input_phone), expected_output)
    
    def test_invalid_phone_formats(self):
        # Test invalid phone formats
        test_cases = [
            "12345",  # Too short
            "1234567890123",  # Too long
            "abcdefghij",  # Non-numeric
            "380291234567",  # Wrong country code
        ]
        
        for phone in test_cases:
            with self.assertRaises(ValidationError):
                validate_and_format_phone(phone)