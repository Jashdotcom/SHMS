from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at")
    search_fields = ("title", "message", "created_by__username")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
