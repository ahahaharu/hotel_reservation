from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date


class Client(models.Model):
    """Client model representing hotel guests"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate age based on date of birth"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

class RoomCategory(models.Model):
    """Model for different categories of rooms"""
    name = models.CharField(max_length=50)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.ManyToManyField('Amenity', related_name='room_categories', blank=True)
    
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
    has_children = models.BooleanField(default=False, verbose_name="Staying with children")  # Новое поле
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reservation for {self.client} - Room {self.room.room_number}"
    
    def calculate_total_price(self):
        """Calculate total price based on duration and room price"""
        days = (self.check_out_date - self.check_in_date).days
        return self.room.category.base_price * days
    
class Article(models.Model):
    """Model for news articles"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    summary = models.TextField(max_length=500)
    image = models.ImageField(upload_to='article_images/', blank=True, null=True)
    published_date = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', related_name='articles', blank=True)
    
    class Meta:
        ordering = ['-published_date']
    
    def __str__(self):
        return self.title

class CompanyInfo(models.Model):
    """Model for company information"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    history = models.TextField(blank=True, null=True)
    foundation_year = models.PositiveIntegerField(blank=True, null=True)
    legal_info = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Company Information"
    
    def __str__(self):
        return self.name

class FAQ(models.Model):
    """Model for frequently asked questions"""
    question = models.CharField(max_length=300)
    answer = models.TextField()
    date_added = models.DateField(default=timezone.now)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return self.question

class Staff(models.Model):
    """Model for staff/employee information"""
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='staff/', blank=True, null=True)
    description = models.TextField()
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = "Staff"
    
    def __str__(self):
        return f"{self.name} - {self.position}"

class Vacancy(models.Model):
    """Model for job vacancies"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    salary = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_posted = models.DateField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Vacancies"
    
    def __str__(self):
        return self.title

class Review(models.Model):
    """Model for customer reviews"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    text = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_posted']
    
    def __str__(self):
        return f"Review by {self.client} - {self.rating} stars"

class PromoCode(models.Model):
    """Model for promotional codes"""
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    discount_percent = models.PositiveSmallIntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateField()
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code
    
    @property
    def is_valid(self):
        today = timezone.now().date()
        return self.is_active and self.valid_from <= today <= self.valid_to

class Amenity(models.Model):
    """Model for hotel amenities/facilities"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Font awesome icon name")
    
    class Meta:
        verbose_name_plural = "Amenities"
    
    def __str__(self):
        return self.name

class Service(models.Model):
    """Model for hotel services"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    """Model for article tags"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class ServiceBooking(models.Model):
    """Model for booking additional services"""
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='service_booking')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='service_bookings')
    services = models.ManyToManyField(Service, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Service booking for {self.reservation}"

class ChartImage(models.Model):
    """Model for storing chart images"""
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='charts/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Banner(models.Model):
    """Model for promotional banners on the home page"""
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Partner(models.Model):
    """Model for partner companies"""
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partners/')
    website_url = models.URLField()
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Cart(models.Model):
    """Shopping cart model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart for session {self.session_key}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    """Item in a shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.service.name} in cart"

    @property
    def total_price(self):
        return self.service.price * self.quantity

class Order(models.Model):
    """Order model for completed purchases"""
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    email = models.EmailField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.email}"

class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.service.name}"

    @property
    def total_price(self):
        return self.price * self.quantity