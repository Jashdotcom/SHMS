from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
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
	qr_code = models.ImageField(upload_to="bookings/qr_codes/", blank=True, null=True)
	check_in_at = models.DateTimeField(blank=True, null=True)
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

	def generate_qr_code(self):
		import qrcode

		payload = (
			f"booking_id={self.pk};"
			f"user_id={self.user_id};"
			f"room_id={self.room_id};"
			f"bed_id={self.bed_id};"
			f"start_date={self.start_date};"
			f"end_date={self.end_date}"
		)
		qr_image = qrcode.make(payload)

		buffer = BytesIO()
		qr_image.save(buffer, format="PNG")
		file_name = f"booking_{self.pk}.png"
		self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)

	def save(self, *args, **kwargs):
		self.full_clean()
		is_new = self.pk is None
		previous = None
		if self.pk:
			previous = Booking.objects.filter(pk=self.pk).values("status", "bed_id").first()

		super().save(*args, **kwargs)

		if is_new and not self.qr_code:
			self.generate_qr_code()
			super().save(update_fields=["qr_code"])

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
