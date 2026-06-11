from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from core.emails import send_templated_email
from core.notifications import create_notification
from payments.models import Payment

from bookings.models import Booking


class Command(BaseCommand):
    help = "Expire unpaid bookings that passed the configured hold time."

    def handle(self, *args, **options):
        now = timezone.now()
        expiry_hours = getattr(settings, "BOOKING_EXPIRY_HOURS", 24)
        cutoff = now - timedelta(hours=expiry_hours)

        expired_bookings = (
            Booking.objects.select_related("user", "room", "bed")
            .filter(status=Booking.STATUS_BOOKED)
            .filter(Q(expires_at__lte=now) | Q(expires_at__isnull=True, created_at__lte=cutoff))
        )

        expired_count = 0
        for booking in expired_bookings:
            has_paid_payment = Payment.objects.filter(user=booking.user, status=Payment.STATUS_PAID).exists()
            if has_paid_payment:
                continue

            booking.status = Booking.STATUS_CANCELLED
            booking.save(update_fields=["status"])
            expired_count += 1

            message = (
                f"Your booking for Room {booking.room.room_number} and Bed {booking.bed.bed_number} "
                f"has expired because payment was not completed in time."
            )
            if booking.user.email:
                send_templated_email(
                    subject="Booking Expired | SHMS",
                    template_name="emails/notification.html",
                    context={"title": "Booking expired", "message": message, "action_url": ""},
                    recipients=[booking.user.email],
                )
            create_notification(recipient=booking.user, title="Booking expired", message=message)

        self.stdout.write(self.style.SUCCESS(f"Expired {expired_count} unpaid booking(s)."))
