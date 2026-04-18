from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ("user", "room", "bed", "start_date", "end_date", "status", "created_at")
	list_filter = ("status", "start_date", "end_date")
	search_fields = ("user__username", "room__room_number", "bed__bed_number")
