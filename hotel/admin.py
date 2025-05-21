from django.contrib import admin
from .models import Article, Client, RoomCategory, Room, RoomImage, Reservation, CompanyInfo, FAQ, Staff, Vacancy, Review, PromoCode, Amenity, Service, Tag, ServiceBooking

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price')
    filter_horizontal = ('amenities',)  # Makes it easier to manage many-to-many

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'category', 'status', 'capacity')
    list_filter = ('category', 'status')
    inlines = [RoomImageInline]

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('client', 'room', 'check_in_date', 'check_out_date', 'status')
    list_filter = ('status', 'check_in_date')
    date_hierarchy = 'check_in_date'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'is_published')
    list_filter = ('is_published', 'published_date', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    filter_horizontal = ('tags',)  # Makes it easier to manage many-to-many

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'foundation_year')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'date_added', 'order')
    list_filter = ('date_added',)
    search_fields = ('question', 'answer')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'email', 'phone', 'order')
    search_fields = ('name', 'position')
    list_filter = ('position',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'date_posted')
    list_filter = ('is_active', 'date_posted')
    search_fields = ('title', 'description')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client', 'rating', 'date_posted', 'is_published')
    list_filter = ('rating', 'is_published', 'date_posted')
    search_fields = ('text', 'client__first_name', 'client__last_name')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'discount_amount', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('is_active', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name', 'description')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'client', 'booking_date', 'total_price')
    filter_horizontal = ('services',)  # Makes it easier to manage many-to-many