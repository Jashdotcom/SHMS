from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from hostel.models import Room

from .forms import BookingForm
from .models import Booking


@login_required
def book_room_view(request):
	rooms = Room.objects.all().prefetch_related("beds").order_by("room_number")

	if request.method == "POST":
		form = BookingForm(request.POST)
		if form.is_valid():
			with transaction.atomic():
				booking = form.save(commit=False)
				booking.user = request.user
				booking.status = Booking.STATUS_BOOKED
				booking.save()

			messages.success(request, "Booking created successfully. QR code generated.")
			return redirect("bookings:qr", booking_id=booking.id)
	else:
		form = BookingForm()

	return render(request, "bookings/book_room.html", {"form": form, "rooms": rooms})


@login_required
def booking_history_view(request):
	bookings = Booking.objects.select_related("user", "room", "bed", "room__hostel")
	if request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		bookings = bookings.filter(user=request.user)

	return render(request, "bookings/history.html", {"bookings": bookings})


@login_required
def booking_qr_view(request, booking_id):
	booking = get_object_or_404(Booking.objects.select_related("user", "room", "bed", "room__hostel"), pk=booking_id)

	if booking.user != request.user and request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		messages.error(request, "You are not allowed to view this booking QR.")
		return redirect("bookings:history")

	return render(request, "bookings/booking_qr.html", {"booking": booking, "today": date.today()})


@login_required
def check_in_view(request, booking_id):
	booking = get_object_or_404(Booking.objects.select_related("user", "room", "bed", "room__hostel"), pk=booking_id)

	if booking.user != request.user and request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		messages.error(request, "You are not allowed to check in for this booking.")
		return redirect("bookings:history")

	if request.method == "POST":
		today = date.today()
		if today < booking.start_date or today > booking.end_date:
			messages.warning(request, "Check-in is only available during the booking period.")
		elif booking.status != Booking.STATUS_BOOKED:
			messages.warning(request, "Only active bookings can be checked in.")
		elif booking.check_in_at:
			messages.info(request, "Check-in is already marked for this booking.")
		else:
			booking.check_in_at = timezone.now()
			booking.save(update_fields=["check_in_at"])
			messages.success(request, "Check-in marked successfully.")
		return redirect("bookings:check_in", booking_id=booking.id)

	return render(request, "bookings/check_in.html", {"booking": booking})


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
