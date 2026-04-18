from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from bookings.models import Booking
from hostel.models import Bed, Hostel, Room
from payments.models import Payment
from services.models import Complaint, ServiceRequest


class Command(BaseCommand):
    help = "Seed demo data for Smart Hostel Management System"

    def handle(self, *args, **options):
        user_model = get_user_model()

        admin_user, _ = user_model.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@homs.local",
                "first_name": "System",
                "last_name": "Admin",
                "role": user_model.ROLE_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if not admin_user.check_password("admin123"):
            admin_user.set_password("admin123")
            admin_user.save(update_fields=["password"])

        students = []
        for idx in range(1, 6):
            student, _ = user_model.objects.get_or_create(
                username=f"student{idx}",
                defaults={
                    "email": f"student{idx}@homs.local",
                    "first_name": f"Student{idx}",
                    "last_name": "User",
                    "role": user_model.ROLE_STUDENT,
                },
            )
            if not student.check_password("student123"):
                student.set_password("student123")
                student.save(update_fields=["password"])
            students.append(student)

        main_hostel, _ = Hostel.objects.get_or_create(name="Maple Residency", defaults={"location": "Campus Road"})

        created_rooms = []
        for room_no, room_type, capacity in [
            ("A-101", Room.TYPE_DOUBLE, 2),
            ("A-102", Room.TYPE_TRIPLE, 3),
            ("B-201", Room.TYPE_DORM, 4),
        ]:
            room, _ = Room.objects.get_or_create(
                hostel=main_hostel,
                room_number=room_no,
                defaults={"room_type": room_type, "capacity": capacity},
            )
            created_rooms.append(room)
            for bed_index in range(1, room.capacity + 1):
                Bed.objects.get_or_create(room=room, bed_number=f"B{bed_index}", defaults={"is_available": True})

        available_beds = list(Bed.objects.filter(is_available=True).select_related("room")[: len(students)])
        start = date.today()
        end = start + timedelta(days=120)

        for student, bed in zip(students, available_beds):
            booking, created = Booking.objects.get_or_create(
                user=student,
                room=bed.room,
                bed=bed,
                defaults={
                    "start_date": start,
                    "end_date": end,
                    "status": Booking.STATUS_BOOKED,
                },
            )
            if created:
                booking.save()

        for idx, student in enumerate(students, start=1):
            status = [Payment.STATUS_PAID, Payment.STATUS_PARTIAL, Payment.STATUS_UNPAID][idx % 3]
            Payment.objects.get_or_create(
                user=student,
                amount=Decimal("4500.00") + Decimal(idx * 500),
                status=status,
            )

            Complaint.objects.get_or_create(
                user=student,
                issue=f"Complaint sample {idx}: Wi-Fi connectivity issue in corridor.",
                defaults={"status": Complaint.STATUS_OPEN},
            )

            ServiceRequest.objects.get_or_create(
                user=student,
                request_type=ServiceRequest.TYPE_CLEANING if idx % 2 == 0 else ServiceRequest.TYPE_MAINTENANCE,
                details="Demo service request for hostel operations.",
                defaults={"status": ServiceRequest.STATUS_REQUESTED},
            )

        self.stdout.write(self.style.SUCCESS("Demo seed completed."))
        self.stdout.write("Admin login: username=admin, password=admin123")
        self.stdout.write("Student login sample: username=student1, password=student123")
