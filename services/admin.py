from django.contrib import admin

from .models import Complaint, ServiceRequest


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
	list_display = ("user", "status", "created_at", "updated_at")
	list_filter = ("status", "created_at")
	search_fields = ("user__username", "issue")


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
	list_display = ("user", "request_type", "status", "created_at", "updated_at")
	list_filter = ("request_type", "status", "created_at")
	search_fields = ("user__username", "details")
