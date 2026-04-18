from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ("user", "amount", "due_date", "paid_date", "late_fee", "status", "date")
	list_filter = ("status", "date", "due_date")
	search_fields = ("user__username", "user__email")
	readonly_fields = ("late_fee", "date", "updated_at")
	fieldsets = (
		("Payment Info", {"fields": ("user", "amount", "status")}),
		("Dates", {"fields": ("due_date", "paid_date", "date", "updated_at")}),
		("Late Fee", {"fields": ("late_fee",)}),
	)
