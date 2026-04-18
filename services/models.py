from django.conf import settings
from django.db import models


class Complaint(models.Model):
	STATUS_PENDING = "pending"
	STATUS_IN_PROGRESS = "in_progress"
	STATUS_RESOLVED = "resolved"

	STATUS_CHOICES = [
		(STATUS_PENDING, "Pending"),
		(STATUS_IN_PROGRESS, "In Progress"),
		(STATUS_RESOLVED, "Resolved"),
	]

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="complaints")
	issue = models.TextField()
	image = models.ImageField(upload_to="complaints/", null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Complaint by {self.user.username} ({self.get_status_display()})"

	def get_status_badge_class(self):
		if self.status == self.STATUS_PENDING:
			return "warning"
		elif self.status == self.STATUS_IN_PROGRESS:
			return "info"
		elif self.status == self.STATUS_RESOLVED:
			return "success"
		return "secondary"


class ServiceRequest(models.Model):
	TYPE_CLEANING = "cleaning"
	TYPE_MAINTENANCE = "maintenance"

	REQUEST_TYPE_CHOICES = [
		(TYPE_CLEANING, "Cleaning"),
		(TYPE_MAINTENANCE, "Maintenance"),
	]

	STATUS_REQUESTED = "requested"
	STATUS_IN_PROGRESS = "in_progress"
	STATUS_COMPLETED = "completed"

	STATUS_CHOICES = [
		(STATUS_REQUESTED, "Requested"),
		(STATUS_IN_PROGRESS, "In Progress"),
		(STATUS_COMPLETED, "Completed"),
	]

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_requests")
	request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
	details = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.get_request_type_display()} request by {self.user.username}"
