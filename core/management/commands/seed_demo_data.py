from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from accounts.models import User
from hostel.models import Hostel, Room, Bed
from bookings.models import Booking
from payments.models import Payment
from announcements.models import Announcement
from services.models import Complaint, ServiceRequest
from core.models import Notification


class Command(BaseCommand):
    help = "Create realistic demo data for SHMS"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Creating SHMS demo data..."))

        User = get_user_model()

        # ---------------------------------------------------------
        # 1. ADMIN
        # ---------------------------------------------------------

        admin, created = User.objects.get_or_create(
            username="demo_admin",
            defaults={
                "email": "demo.admin@smarthostel.com",
                "first_name": "Demo",
                "last_name": "Admin",
                "role": User.ROLE_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            admin.set_password("DemoAdmin@123")
            admin.save()

        # ---------------------------------------------------------
        # 2. STUDENTS
        # ---------------------------------------------------------

        students = []

        student_data = [
            ("rahul.sharma", "Rahul", "Sharma"),
            ("priya.patel", "Priya", "Patel"),
            ("rohan.mehta", "Rohan", "Mehta"),
            ("ananya.desai", "Ananya", "Desai"),
            ("arjun.shah", "Arjun", "Shah"),
            ("neha.verma", "Neha", "Verma"),
            ("vivek.joshi", "Vivek", "Joshi"),
            ("isha.patel", "Isha", "Patel"),
            ("aditya.rao", "Aditya", "Rao"),
            ("simran.kapoor", "Simran", "Kapoor"),
        ]

        for username, first_name, last_name in student_data:
            student, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": User.ROLE_STUDENT,
                },
            )

            if created:
                student.set_password("Student@123")
                student.save()

            students.append(student)

        self.stdout.write(
            self.style.SUCCESS(f"Students ready: {len(students)}")
        )

        # ---------------------------------------------------------
        # 3. HOSTELS
        # ---------------------------------------------------------

        hostel1, _ = Hostel.objects.get_or_create(
            name="Smart Hostel Boys",
            defaults={
                "location": "Mumbai Campus",
            },
        )

        hostel2, _ = Hostel.objects.get_or_create(
            name="Smart Hostel Girls",
            defaults={
                "location": "Mumbai Campus",
            },
        )

        hostels = [hostel1, hostel2]

        # ---------------------------------------------------------
        # 4. ROOMS + BEDS
        # ---------------------------------------------------------

        room_definitions = [
            ("101", Room.TYPE_SINGLE),
            ("102", Room.TYPE_DOUBLE),
            ("103", Room.TYPE_TRIPLE),
            ("104", Room.TYPE_DORM),
            ("105", Room.TYPE_DOUBLE),
            ("106", Room.TYPE_TRIPLE),
            ("107", Room.TYPE_SINGLE),
            ("108", Room.TYPE_DORM),
        ]

        rooms = []

        for hostel in hostels:
            for room_number, room_type in room_definitions:

                room, created = Room.objects.get_or_create(
                    hostel=hostel,
                    room_number=room_number,
                    defaults={
                        "room_type": room_type,
                        "capacity": 0,
                        "available_beds": 0,
                    },
                )

                if created:
                    room.room_type = room_type
                    room.capacity = 0
                    room.available_beds = 0
                    room.save()

                    for number in range(1, room.capacity + 1):
                        Bed.objects.create(
                            room=room,
                            bed_number=f"B{number}",
                            is_available=True,
                        )

                    room.available_beds = room.capacity
                    room.save(update_fields=["available_beds"])

                else:
                    # Make sure existing rooms have their beds.
                    existing_beds = room.beds.count()

                    if existing_beds == 0:
                        for number in range(1, room.capacity + 1):
                            Bed.objects.create(
                                room=room,
                                bed_number=f"B{number}",
                                is_available=True,
                            )

                    room.available_beds = room.beds.filter(
                        is_available=True
                    ).count()

                    room.save(update_fields=["available_beds"])

                rooms.append(room)

        self.stdout.write(
            self.style.SUCCESS(f"Hostels ready: {len(hostels)}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Rooms ready: {len(rooms)}")
        )

        # ---------------------------------------------------------
        # 5. BOOKINGS
        # ---------------------------------------------------------

        today = timezone.localdate()

        booked_students = students[:7]

        for index, student in enumerate(booked_students):

            room = rooms[index]

            bed = room.beds.filter(is_available=True).first()

            if not bed:
                continue

            existing_booking = Booking.objects.filter(
                user=student,
                status=Booking.STATUS_BOOKED,
            ).first()

            if existing_booking:
                continue

            booking = Booking(
                user=student,
                room=room,
                bed=bed,
                start_date=today - timedelta(days=5),
                end_date=today + timedelta(days=90),
                status=Booking.STATUS_BOOKED,
                check_in_at=timezone.now() - timedelta(days=5),
            )

            booking.save()

        # Completed bookings
        for index, student in enumerate(students[7:9]):

            room = rooms[index + 7]

            bed = room.beds.first()

            if not bed:
                continue

            if Booking.objects.filter(
                user=student,
                status=Booking.STATUS_COMPLETED,
            ).exists():
                continue

            Booking.objects.create(
                user=student,
                room=room,
                bed=bed,
                start_date=today - timedelta(days=120),
                end_date=today - timedelta(days=30),
                status=Booking.STATUS_COMPLETED,
                check_in_at=timezone.now() - timedelta(days=120),
            )

        # Cancelled booking
        student = students[9]
        room = rooms[10]
        bed = room.beds.first()

        if bed and not Booking.objects.filter(
            user=student,
            status=Booking.STATUS_CANCELLED,
        ).exists():

            Booking.objects.create(
                user=student,
                room=room,
                bed=bed,
                start_date=today - timedelta(days=60),
                end_date=today - timedelta(days=10),
                status=Booking.STATUS_CANCELLED,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Bookings ready: {Booking.objects.count()}"
            )
        )

        # ---------------------------------------------------------
        # 6. PAYMENTS
        # ---------------------------------------------------------

        payment_data = [
            (students[0], Decimal("12000"), Payment.STATUS_PAID),
            (students[1], Decimal("12000"), Payment.STATUS_PAID),
            (students[2], Decimal("10000"), Payment.STATUS_PARTIAL),
            (students[3], Decimal("12000"), Payment.STATUS_PAID),
            (students[4], Decimal("10000"), Payment.STATUS_UNPAID),
            (students[5], Decimal("12000"), Payment.STATUS_PAID),
            (students[6], Decimal("10000"), Payment.STATUS_PARTIAL),
            (students[7], Decimal("12000"), Payment.STATUS_UNPAID),
            (students[8], Decimal("10000"), Payment.STATUS_PAID),
            (students[9], Decimal("12000"), Payment.STATUS_UNPAID),
        ]

        for student, amount, status in payment_data:

            if Payment.objects.filter(
                user=student,
                amount=amount,
            ).exists():
                continue

            payment = Payment(
                user=student,
                amount=amount,
                status=status,
                due_date=today + timedelta(days=15),
            )

            if status == Payment.STATUS_PAID:
                payment.paid_date = timezone.now()

            payment.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Payments ready: {Payment.objects.count()}"
            )
        )

        # ---------------------------------------------------------
        # 7. ANNOUNCEMENTS
        # ---------------------------------------------------------

        announcements = [
            (
                "Hostel Maintenance Schedule",
                "Routine maintenance will be carried out this weekend."
            ),
            (
                "Mess Timing Update",
                "Dinner will be served from 7:30 PM to 9:30 PM."
            ),
            (
                "Room Inspection",
                "Monthly room inspection will be conducted next week."
            ),
            (
                "Sports Event",
                "Inter-hostel sports registrations are now open."
            ),
            (
                "Fee Payment Reminder",
                "Students with pending hostel fees are requested to complete payment."
            ),
        ]

        for title, message in announcements:

            Announcement.objects.get_or_create(
                title=title,
                defaults={
                    "message": message,
                    "created_by": admin,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Announcements ready: {Announcement.objects.count()}"
            )
        )

        # ---------------------------------------------------------
        # 8. COMPLAINTS
        # ---------------------------------------------------------

        complaints = [
            (
                students[0],
                "The bathroom tap in my room is leaking.",
                Complaint.STATUS_PENDING,
            ),
            (
                students[1],
                "The room fan is making unusual noise.",
                Complaint.STATUS_IN_PROGRESS,
            ),
            (
                students[2],
                "The corridor light near my room is not working.",
                Complaint.STATUS_RESOLVED,
            ),
            (
                students[3],
                "There is a water supply issue in the washroom.",
                Complaint.STATUS_PENDING,
            ),
            (
                students[4],
                "The cupboard door needs repair.",
                Complaint.STATUS_RESOLVED,
            ),
        ]

        for student, issue, status in complaints:

            Complaint.objects.get_or_create(
                user=student,
                issue=issue,
                defaults={
                    "status": status,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Complaints ready: {Complaint.objects.count()}"
            )
        )

        # ---------------------------------------------------------
        # 9. SERVICE REQUESTS
        # ---------------------------------------------------------

        services = [
            (
                students[0],
                ServiceRequest.TYPE_CLEANING,
                "Please clean the room and bathroom.",
                ServiceRequest.STATUS_REQUESTED,
            ),
            (
                students[1],
                ServiceRequest.TYPE_MAINTENANCE,
                "Please check the electrical socket near the study table.",
                ServiceRequest.STATUS_IN_PROGRESS,
            ),
            (
                students[2],
                ServiceRequest.TYPE_CLEANING,
                "Requesting room cleaning.",
                ServiceRequest.STATUS_COMPLETED,
            ),
            (
                students[3],
                ServiceRequest.TYPE_MAINTENANCE,
                "Please repair the broken cupboard handle.",
                ServiceRequest.STATUS_REQUESTED,
            ),
            (
                students[4],
                ServiceRequest.TYPE_CLEANING,
                "Bathroom cleaning required.",
                ServiceRequest.STATUS_COMPLETED,
            ),
        ]

        for student, request_type, details, status in services:

            ServiceRequest.objects.get_or_create(
                user=student,
                request_type=request_type,
                details=details,
                defaults={
                    "status": status,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Service requests ready: {ServiceRequest.objects.count()}"
            )
        )

        # ---------------------------------------------------------
        # 10. NOTIFICATIONS
        # ---------------------------------------------------------

        notifications = [
            (
                students[0],
                "Booking Confirmed",
                "Your hostel booking has been confirmed.",
                Notification.TYPE_SUCCESS,
            ),
            (
                students[1],
                "Payment Reminder",
                "Your hostel payment is due soon.",
                Notification.TYPE_WARNING,
            ),
            (
                students[2],
                "Announcement",
                "A new hostel announcement has been posted.",
                Notification.TYPE_INFO,
            ),
            (
                students[3],
                "Complaint Update",
                "Your complaint is currently being processed.",
                Notification.TYPE_INFO,
            ),
            (
                students[4],
                "Service Completed",
                "Your service request has been completed.",
                Notification.TYPE_SUCCESS,
            ),
        ]

        for student, title, message, notification_type in notifications:

            Notification.objects.get_or_create(
                recipient=student,
                title=title,
                defaults={
                    "message": message,
                    "notification_type": notification_type,
                    "is_read": False,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Notifications ready: {Notification.objects.count()}"
            )
        )

        # ---------------------------------------------------------
        # FINISHED
        # ---------------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "========================================"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "SHMS DEMO DATA CREATED SUCCESSFULLY"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "========================================"
            )
        )

        self.stdout.write(
            f"Users:          {User.objects.count()}"
        )
        self.stdout.write(
            f"Hostels:        {Hostel.objects.count()}"
        )
        self.stdout.write(
            f"Rooms:          {Room.objects.count()}"
        )
        self.stdout.write(
            f"Beds:           {Bed.objects.count()}"
        )
        self.stdout.write(
            f"Bookings:       {Booking.objects.count()}"
        )
        self.stdout.write(
            f"Payments:       {Payment.objects.count()}"
        )
        self.stdout.write(
            f"Announcements:  {Announcement.objects.count()}"
        )
        self.stdout.write(
            f"Complaints:     {Complaint.objects.count()}"
        )
        self.stdout.write(
            f"Services:       {ServiceRequest.objects.count()}"
        )
        self.stdout.write(
            f"Notifications:  {Notification.objects.count()}"
        )