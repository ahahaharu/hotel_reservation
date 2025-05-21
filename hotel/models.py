from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    """Client model representing hotel guests"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class RoomCategory(models.Model):
    """Model for different categories of rooms"""
    name = models.CharField(max_length=50)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name_plural = "Room Categories"
    
    def __str__(self):
        return self.name

class Room(models.Model):
    """Model representing individual hotel rooms"""
    ROOM_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
    ]
    
    room_number = models.CharField(max_length=10, unique=True)
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name='rooms')
    status = models.CharField(max_length=15, choices=ROOM_STATUS, default='available')
    capacity = models.PositiveSmallIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Room {self.room_number} ({self.category.name})"

class RoomImage(models.Model):
    """Model for storing room images"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/')
    caption = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Image for {self.room}"

class Reservation(models.Model):
    """Model for room reservations"""
    RESERVATION_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=15, choices=RESERVATION_STATUS, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reservation for {self.client} - Room {self.room.room_number}"
    
    def calculate_total_price(self):
        """Calculate total price based on duration and room price"""
        days = (self.check_out_date - self.check_in_date).days
        return self.room.category.base_price * days