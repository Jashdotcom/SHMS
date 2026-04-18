from django.conf import settings
from django.db import models


class Payment(models.Model):
	STATUS_PAID = "paid"
	STATUS_PARTIAL = "partial"
	STATUS_UNPAID = "unpaid"

	STATUS_CHOICES = [
		(STATUS_PAID, "Paid"),
		(STATUS_PARTIAL, "Partial"),
		(STATUS_UNPAID, "Unpaid"),
	]

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNPAID)
	date = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]

	def __str__(self):
		return f"{self.user.username} - {self.amount} ({self.get_status_display()})"
