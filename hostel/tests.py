from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Hostel, Room


class RoomListViewTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username="room-list-user",
			password="password",
		)
		self.hostel = Hostel.objects.create(name="Test Hostel", location="Test Location")

	def test_only_rooms_with_available_beds_are_displayed(self):
		empty_room = Room.objects.create(
			hostel=self.hostel,
			room_number="A-101",
			room_type=Room.TYPE_SINGLE,
			capacity=1,
			available_beds=0,
		)
		available_room = Room.objects.create(
			hostel=self.hostel,
			room_number="A-102",
			room_type=Room.TYPE_DOUBLE,
			capacity=2,
			available_beds=1,
		)
		self.client.force_login(self.user)

		response = self.client.get(reverse("hostel:rooms"))

		self.assertNotContains(response, empty_room.room_number)
		self.assertContains(response, available_room.room_number)
