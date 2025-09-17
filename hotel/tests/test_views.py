from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth.models import User
from hotel.models import (
    RoomCategory, Room, Client, Reservation, CompanyInfo,
    Article, FAQ, Staff, Vacancy, Review, PromoCode, Service
)
from datetime import date, timedelta

class HomeViewTest(TestCase):
    def setUp(self):
        self.client = TestClient()
        
        # Create an article for the home page
        self.article = Article.objects.create(
            title="Test Article",
            slug="test-article",
            content="This is a test article",
            summary="Test summary",
            is_published=True
        )
    
    def test_home_view(self):
        response = self.client.get(reverse('hotel:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hotel/home.html')
        self.assertContains(response, "Welcome to LuxStay Hotel")
        
        # Check if the latest article is displayed
        self.assertContains(response, "Test Article")
        self.assertContains(response, "Test summary")

class RoomViewsTest(TestCase):
    def setUp(self):
        self.client = TestClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpassword',
            is_staff=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            password='userpassword'
        )
        
        # Create client for regular user
        self.regular_client = Client.objects.create(
            user=self.regular_user,
            first_name='Regular',
            last_name='User',
            email='regular@example.com',
            phone='+375 (29) 123-45-67',
            date_of_birth=date(1990, 1, 1)
        )
        
        # Create room category
        self.category = RoomCategory.objects.create(
            name='Standard',
            description='Standard room',
            base_price=100.00
        )
        
        # Create room
        self.room = Room.objects.create(
            room_number='101',
            category=self.category,
            status='available',
            capacity=2,
            description='Nice room'
        )
    
    def test_room_list_view(self):
        response = self.client.get(reverse('hotel:room_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hotel/room_list.html')
        self.assertContains(response, 'Room 101')
        self.assertContains(response, 'Standard')
        
    def test_room_detail_view(self):
        response = self.client.get(reverse('hotel:room_detail', args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hotel/room_detail.html')
        self.assertContains(response, 'Room 101')
        self.assertContains(response, 'Nice room')
        
    def test_room_create_view_unauthenticated(self):
        # Unauthenticated users should be redirected to login
        response = self.client.get(reverse('hotel:room_create'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
    def test_room_create_view_not_staff(self):
        # Non-staff users should be redirected
        self.client.login(username='user', password='userpassword')
        response = self.client.get(reverse('hotel:room_create'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
    def test_room_create_view_staff(self):
        # Staff users should access the create form
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('hotel:room_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hotel/room_form.html')
    
    def test_client_dashboard_authenticated(self):
        self.client.login(username='user', password='userpassword')
        response = self.client.get(reverse('hotel:client_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hotel/client/dashboard.html')
        self.assertContains(response, 'Regular User')
    
    def test_client_dashboard_unauthenticated(self):
        response = self.client.get(reverse('hotel:client_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

class BookRoomViewTest(TestCase):
    def setUp(self):
        self.client = TestClient()
        
        # Create user and client
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        
        self.client_user = Client.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='+375 (29) 123-45-67',
            date_of_birth=date(1990, 1, 1)
        )
        
        # Create room category and room
        self.category = RoomCategory.objects.create(
            name='Standard',
            description='Standard room',
            base_price=100.00
        )
        
        self.room = Room.objects.create(
            room_number='101',
            category=self.category,
            status='available',
            capacity=2
        )
    
    def test_book_room_unauthenticated(self):
        response = self.client.get(reverse('hotel:book_room', args=[self.room.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_book_room_form_display(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('hotel:book_room', args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hotel/client/book_room.html')
        
    def test_book_room_valid_submission(self):
        self.client.login(username='testuser', password='password123')
        
        today = date.today()
        check_in = (today + timedelta(days=1)).strftime('%Y-%m-%d')
        check_out = (today + timedelta(days=3)).strftime('%Y-%m-%d')
        
        response = self.client.post(reverse('hotel:book_room', args=[self.room.pk]), {
            'check_in_date': check_in,
            'check_out_date': check_out,
            'special_requests': 'Need extra pillows'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        
        # Verify reservation was created
        reservation = Reservation.objects.filter(client=self.client_user, room=self.room).first()
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.status, 'confirmed')
        self.assertEqual(reservation.special_requests, 'Need extra pillows')
        
        # Verify room status was updated
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, 'reserved')

class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = TestClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
    
    def test_login_view(self):
        response = self.client.get(reverse('hotel:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hotel/auth/login.html')
    
    def test_login_valid_submission(self):
        response = self.client.post(reverse('hotel:login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
    def test_login_invalid_submission(self):
        response = self.client.post(reverse('hotel:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, "Please enter a correct username and password")
    
    def test_register_view(self):
        response = self.client.get(reverse('hotel:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hotel/auth/register.html')
    
    def test_logout_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('hotel:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout