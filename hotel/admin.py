from django.contrib import admin
from .models import (
    Article, Client, RoomCategory, Room, RoomImage, Reservation, CompanyInfo, FAQ, Staff, 
    Vacancy, Review, PromoCode, Amenity, Service, Tag, ServiceBooking, ChartImage,
    Banner, Partner, Cart, CartItem, Order, OrderItem, CompanyHistory
)

def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
make_active.short_description = "Mark selected items as active"

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
make_inactive.short_description = "Mark selected items as inactive"

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('rating', 'text', 'date_posted', 'is_published')
    readonly_fields = ('date_posted',)

class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 0
    fields = ('room', 'check_in_date', 'check_out_date', 'status', 'total_price')

class ServiceBookingInline(admin.TabularInline):
    model = ServiceBooking
    extra = 0
    fields = ('booking_date', 'total_price', 'notes')
    readonly_fields = ('booking_date',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'formatted_phone', 'get_age')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    inlines = [ReservationInline, ReviewInline]
    
    def formatted_phone(self, obj):
        return obj.phone
    formatted_phone.short_description = 'Phone Number'
    
    def get_age(self, obj):
        return obj.age if obj.age is not None else "N/A"
    get_age.short_description = 'Age'

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price')
    filter_horizontal = ('amenities',)  

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'category', 'status', 'capacity')
    list_filter = ('category', 'status')
    inlines = [RoomImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('room_number', 'category', 'capacity')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)  # This section can be collapsed
        }),
    )

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('client', 'room', 'check_in_date', 'check_out_date', 'status', 'has_children')
    list_filter = ('status', 'check_in_date', 'has_children', 'client')
    date_hierarchy = 'check_in_date'
    inlines = [ServiceBookingInline]
    readonly_fields = ('created_at', 'updated_at')

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
    actions = [make_active, make_inactive] 

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
    list_display_links = ('reservation', 'client')  # Make these fields clickable
    filter_horizontal = ('services',)
    search_fields = ('client__first_name', 'client__last_name', 'reservation__room__room_number')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'order')

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website_url')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'items_count', 'created_at')
    readonly_fields = ('created_at',)
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items Count'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'service', 'quantity', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'service', 'quantity', 'price', 'total_price')

@admin.register(CompanyHistory)
class CompanyHistoryAdmin(admin.ModelAdmin):
    list_display = ['company', 'year', 'event']
    list_filter = ['year']
    search_fields = ['event']