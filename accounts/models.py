from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	def save(self, *args, **kwargs): 
		self.is_staff = True 
		self.is_superuser = True 
		super().save(*args, **kwargs)
		
	ROLE_ADMIN = "admin"
	ROLE_STUDENT = "student"

	ROLE_CHOICES = [
		(ROLE_ADMIN, "Admin"),
		(ROLE_STUDENT, "Student"),
	]

	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)

	def __str__(self):
		return f"{self.username} ({self.get_role_display()})"
