from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User

from .forms import BookingForm
from .models import Booking


@login_required
def book_room_view(request):
	if request.method == "POST":
		form = BookingForm(request.POST)
		if form.is_valid():
			booking = form.save(commit=False)
			booking.user = request.user
			booking.status = Booking.STATUS_BOOKED
			booking.save()
			messages.success(request, "Booking created successfully.")
			return redirect("bookings:history")
	else:
		form = BookingForm()

	return render(request, "bookings/book_room.html", {"form": form})


@login_required
def booking_history_view(request):
	bookings = Booking.objects.select_related("user", "room", "bed", "room__hostel")
	if request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		bookings = bookings.filter(user=request.user)

	return render(request, "bookings/history.html", {"bookings": bookings})


@login_required
def cancel_booking_view(request, booking_id):
	booking = get_object_or_404(Booking, pk=booking_id)

	if booking.user != request.user and request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		messages.error(request, "You are not allowed to cancel this booking.")
		return redirect("bookings:history")

	if booking.status == Booking.STATUS_BOOKED:
		booking.status = Booking.STATUS_CANCELLED
		booking.save(update_fields=["status"])
		messages.info(request, "Booking cancelled.")
	else:
		messages.warning(request, "Only active bookings can be cancelled.")

	return redirect("bookings:history")
