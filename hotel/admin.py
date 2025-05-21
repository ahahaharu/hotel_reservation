from django.contrib import admin
from .models import Client, RoomCategory, Room, RoomImage, Reservation

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price')

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