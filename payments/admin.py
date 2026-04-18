from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ("user", "amount", "status", "date", "updated_at")
	list_filter = ("status", "date")
	search_fields = ("user__username", "user__email")
