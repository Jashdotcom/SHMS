from datetime import date

from django.conf import settings
from django.db import models
from django.utils import timezone


class Payment(models.Model):
	STATUS_PAID = "paid"
	STATUS_PARTIAL = "partial"
	STATUS_UNPAID = "unpaid"

	STATUS_CHOICES = [
		(STATUS_PAID, "Paid"),
		(STATUS_PARTIAL, "Partial"),
		(STATUS_UNPAID, "Unpaid"),
	]

	LATE_FEE_PER_DAY = 50  # in currency units (₹)

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	invoice_number = models.CharField(max_length=32, blank=True, null=True, unique=True)
	invoice_generated_at = models.DateTimeField(blank=True, null=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNPAID)
	due_date = models.DateField(null=True, blank=True)
	paid_date = models.DateTimeField(null=True, blank=True)
	late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	date = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]

	def __str__(self):
		return f"{self.user.username} - {self.amount} ({self.get_status_display()})"

	def calculate_late_fee(self):
		"""Calculate late fee based on due_date and paid_date."""
		if not self.due_date or not self.paid_date:
			return 0
		paid_date_only = self.paid_date.date()
		if paid_date_only > self.due_date:
			days_late = (paid_date_only - self.due_date).days
			return days_late * self.LATE_FEE_PER_DAY
		return 0

	def get_total_amount(self):
		"""Return total amount including late fee."""
		return self.amount + self.late_fee

	def save(self, *args, **kwargs):
		if self.status == self.STATUS_PAID and self.paid_date and self.due_date:
			self.late_fee = self.calculate_late_fee()
		is_new = self.pk is None
		super().save(*args, **kwargs)
		if is_new and not self.invoice_number:
			self.invoice_number = f"INV-{timezone.now():%Y%m}-{self.pk:05d}"
			self.invoice_generated_at = timezone.now()
			super().save(update_fields=["invoice_number", "invoice_generated_at"])
