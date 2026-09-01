from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import OuterRef, Subquery
from django.shortcuts import redirect, render

from accounts.models import User

from .forms import RoomForm
from .models import Bed, Room


def _is_admin_user(user):
	return user.is_authenticated and (user.is_staff or user.role == User.ROLE_ADMIN)


@login_required
def room_list_view(request):
	room_ids = Room.objects.filter(
		available_beds__gt=0,
		room_number=OuterRef("room_number"),
	).order_by("-available_beds", "pk").values("pk")[:1]
	rooms = Room.objects.filter(pk=Subquery(room_ids)).select_related("hostel")
	return render(request, "hostel/rooms.html", {"rooms": rooms})


@user_passes_test(_is_admin_user)
def add_room_view(request):
	if request.method == "POST":
		form = RoomForm(request.POST)
		if form.is_valid():
			room = form.save()
			Bed.objects.bulk_create(
				[
					Bed(room=room, bed_number=f"B{i}", is_available=i <= room.available_beds)
					for i in range(1, room.capacity + 1)
				]
			)
			messages.success(request, "Room and beds created successfully.")
			return redirect("hostel:rooms")
	else:
		form = RoomForm()

	return render(request, "hostel/add_room.html", {"form": form})
