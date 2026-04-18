from django.contrib import admin

from .models import Bed, Hostel, Room


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
	list_display = ("name", "location", "created_at")
	search_fields = ("name", "location")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
	list_display = ("hostel", "room_number", "room_type", "capacity")
	list_filter = ("room_type", "hostel")
	search_fields = ("room_number", "hostel__name")


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
	list_display = ("room", "bed_number", "is_available")
	list_filter = ("is_available", "room__hostel")
	search_fields = ("bed_number", "room__room_number")
