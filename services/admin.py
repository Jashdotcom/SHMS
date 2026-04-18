from django.contrib import admin

from .models import Complaint, ServiceRequest


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
	list_display = ("user", "issue_preview", "has_image", "status", "created_at")
	list_filter = ("status", "created_at")
	search_fields = ("user__username", "issue")
	readonly_fields = ("created_at", "updated_at", "image_preview")
	fieldsets = (
		("Complaint Info", {"fields": ("user", "issue", "status")}),
		("Image Proof", {"fields": ("image", "image_preview")}),
		("Timestamps", {"fields": ("created_at", "updated_at")}),
	)

	def issue_preview(self, obj):
		return obj.issue[:50] + "..." if len(obj.issue) > 50 else obj.issue
	issue_preview.short_description = "Issue"

	def has_image(self, obj):
		return "✓" if obj.image else "✗"
	has_image.short_description = "Proof"

	def image_preview(self, obj):
		if obj.image:
			return f'<img src="{obj.image.url}" style="max-width: 300px; max-height: 300px;">'
		return "No image uploaded"
	image_preview.allow_tags = True
	image_preview.short_description = "Image Preview"


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
	list_display = ("user", "request_type", "status", "created_at", "updated_at")
	list_filter = ("request_type", "status", "created_at")
	search_fields = ("user__username", "details")
