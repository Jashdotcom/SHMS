from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Booking(models.Model):
	STATUS_BOOKED = "booked"
	STATUS_CANCELLED = "cancelled"
	STATUS_COMPLETED = "completed"

	STATUS_CHOICES = [
		(STATUS_BOOKED, "Booked"),
		(STATUS_CANCELLED, "Cancelled"),
		(STATUS_COMPLETED, "Completed"),
	]

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
	room = models.ForeignKey("hostel.Room", on_delete=models.PROTECT, related_name="bookings")
	bed = models.ForeignKey("hostel.Bed", on_delete=models.PROTECT, related_name="bookings")
	start_date = models.DateField()
	end_date = models.DateField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BOOKED)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user.username} - {self.room.room_number}/{self.bed.bed_number} ({self.get_status_display()})"

	def clean(self):
		if self.end_date <= self.start_date:
			raise ValidationError("End date must be after start date.")
		if self.bed.room_id != self.room_id:
			raise ValidationError("Selected bed does not belong to the selected room.")

	def save(self, *args, **kwargs):
		self.full_clean()
		previous = None
		if self.pk:
			previous = Booking.objects.filter(pk=self.pk).values("status", "bed_id").first()

		super().save(*args, **kwargs)

		if previous and previous["bed_id"] != self.bed_id:
			from hostel.models import Bed

			old_bed = Bed.objects.filter(pk=previous["bed_id"]).first()
			if old_bed and not old_bed.bookings.filter(status=self.STATUS_BOOKED).exists():
				old_bed.is_available = True
				old_bed.save(update_fields=["is_available"])

		should_be_available = self.status != self.STATUS_BOOKED
		if self.bed.is_available != should_be_available:
			self.bed.is_available = should_be_available
			self.bed.save(update_fields=["is_available"])
