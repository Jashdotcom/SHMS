from django.db import models


class Hostel(models.Model):
	name = models.CharField(max_length=120)
	location = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return f"{self.name} - {self.location}"


class Room(models.Model):
	TYPE_SINGLE = "single"
	TYPE_DOUBLE = "double"
	TYPE_TRIPLE = "triple"
	TYPE_DORM = "dorm"

	ROOM_TYPE_CHOICES = [
		(TYPE_SINGLE, "Single"),
		(TYPE_DOUBLE, "Double"),
		(TYPE_TRIPLE, "Triple"),
		(TYPE_DORM, "Dorm"),
	]

	hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="rooms")
	room_number = models.CharField(max_length=30)
	room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
	capacity = models.PositiveIntegerField()
	available_beds = models.IntegerField(default=0)

	class Meta:
		ordering = ["room_number"]
		unique_together = ("hostel", "room_number")

	def __str__(self):
		return f"{self.hostel.name} - Room {self.room_number}"

	def save(self, *args, **kwargs):
		capacity_by_type = {
			self.TYPE_SINGLE: 1,
			self.TYPE_DOUBLE: 2,
			self.TYPE_TRIPLE: 3,
			self.TYPE_DORM: 4,
		}
		self.capacity = capacity_by_type.get(self.room_type, self.capacity)
		if self.available_beds > self.capacity:
			self.available_beds = self.capacity
		super().save(*args, **kwargs)


class Bed(models.Model):
	room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="beds")
	bed_number = models.CharField(max_length=30)
	is_available = models.BooleanField(default=True)

	class Meta:
		ordering = ["bed_number"]
		unique_together = ("room", "bed_number")

	def __str__(self):
		return f"{self.room.hostel.name} / Room {self.room.room_number} / Bed {self.bed_number}"
