from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from hotel.models import (
    Client, RoomCategory, Room, Reservation, 
    Amenity, Service, PromoCode, Review
)

class ClientModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
        self.client_user = Client.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='+375 (29) 123-45-67',
            date_of_birth=date(1990, 1, 1)
        )

    def test_client_creation(self):
        self.assertEqual(self.client_user.first_name, 'Test')
        self.assertEqual(self.client_user.last_name, 'User')
        self.assertEqual(str(self.client_user), 'Test User')

    def test_client_age_property(self):
        today = date.today()
        expected_age = today.year - 1990 - ((today.month, today.day) < (1, 1))
        self.assertEqual(self.client_user.age, expected_age)
        
    def test_client_age_property_none(self):
        # Test when date_of_birth is None
        client_no_dob = Client.objects.create(
            first_name='No',
            last_name='Birthday',
            email='no_dob@example.com',
            phone='+375 (29) 987-65-43',
            date_of_birth=None
        )
        self.assertIsNone(client_no_dob.age)

class RoomCategoryModelTest(TestCase):
    def setUp(self):
        self.amenity1 = Amenity.objects.create(name='WiFi', description='Free WiFi')
        self.amenity2 = Amenity.objects.create(name='Breakfast', description='Free breakfast')
        
        self.category = RoomCategory.objects.create(
            name='Luxury Suite',
            description='Luxurious suite with all amenities',
            base_price=200.00
        )
        self.category.amenities.add(self.amenity1, self.amenity2)

    def test_room_category_creation(self):
        self.assertEqual(self.category.name, 'Luxury Suite')
        self.assertEqual(self.category.base_price, 200.00)
        self.assertEqual(str(self.category), 'Luxury Suite')
        
    def test_room_category_amenities(self):
        self.assertEqual(self.category.amenities.count(), 2)
        self.assertIn(self.amenity1, self.category.amenities.all())
        self.assertIn(self.amenity2, self.category.amenities.all())

class RoomModelTest(TestCase):
    def setUp(self):
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

    def test_room_creation(self):
        self.assertEqual(self.room.room_number, '101')
        self.assertEqual(self.room.status, 'available')
        self.assertEqual(self.room.capacity, 2)
        self.assertEqual(str(self.room), 'Room 101 (Standard)')

class ReservationModelTest(TestCase):
    def setUp(self):
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
        self.client_user = Client.objects.create(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='+375 (29) 123-45-67',
            date_of_birth=date(1990, 1, 1)
        )
        
        today = date.today()
        self.check_in = today + timedelta(days=1)
        self.check_out = today + timedelta(days=3)
        
        self.reservation = Reservation.objects.create(
            client=self.client_user,
            room=self.room,
            check_in_date=self.check_in,
            check_out_date=self.check_out,
            status='confirmed',
            total_price=200.00
        )

    def test_reservation_creation(self):
        self.assertEqual(self.reservation.client, self.client_user)
        self.assertEqual(self.reservation.room, self.room)
        self.assertEqual(self.reservation.check_in_date, self.check_in)
        self.assertEqual(self.reservation.check_out_date, self.check_out)
        self.assertEqual(self.reservation.status, 'confirmed')
        self.assertEqual(self.reservation.total_price, 200.00)
        
    def test_reservation_calculate_total_price(self):
        calculated_price = self.reservation.calculate_total_price()
        self.assertEqual(calculated_price, 200.00)
        
    def test_reservation_str_representation(self):
        expected_str = f"Reservation for {self.client_user} - Room {self.room.room_number}"
        self.assertEqual(str(self.reservation), expected_str)

class PromoCodeModelTest(TestCase):
    def setUp(self):
        today = date.today()
        self.active_promo = PromoCode.objects.create(
            code="SUMMER2025",
            description="Summer discount",
            discount_percent=10,
            valid_from=today - timedelta(days=5),
            valid_to=today + timedelta(days=5),
            is_active=True
        )
        
        self.expired_promo = PromoCode.objects.create(
            code="WINTER2024",
            description="Winter discount",
            discount_percent=15,
            valid_from=today - timedelta(days=30),
            valid_to=today - timedelta(days=10),
            is_active=True
        )
        
        self.inactive_promo = PromoCode.objects.create(
            code="SPRING2025",
            description="Spring discount",
            discount_percent=20,
            valid_from=today - timedelta(days=5),
            valid_to=today + timedelta(days=5),
            is_active=False
        )

    def test_promo_code_creation(self):
        self.assertEqual(self.active_promo.code, "SUMMER2025")
        self.assertEqual(self.active_promo.discount_percent, 10)
        self.assertEqual(str(self.active_promo), "SUMMER2025")
        
    def test_is_valid_property(self):
        self.assertTrue(self.active_promo.is_valid)
        
        self.assertFalse(self.expired_promo.is_valid)
        
        self.assertFalse(self.inactive_promo.is_valid)