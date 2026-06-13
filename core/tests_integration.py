"""Full integration tests for SHMS routes, roles, APIs, uploads, websockets, and email."""

import io
import json
from datetime import date, timedelta
from decimal import Decimal

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from bookings.models import Booking
from core.models import Notification
from core.notifications import create_notification
from hostel.models import Bed, Hostel, Room
from payments.models import Payment
from services.models import Complaint, ServiceRequest
from SHMS.asgi import application


User = get_user_model()


def _make_image(name="proof.png"):
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


def _make_pdf(name="doc.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4 test", content_type="application/pdf")


class SHMSIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="adminjash",
            password="admin12345",
            email="testadmin@shms.local",
            role=User.ROLE_ADMIN,
            is_staff=True,
        )
        cls.student = User.objects.create_user(
            username="teststudent",
            password="student12345",
            email="teststudent@shms.local",
            role=User.ROLE_STUDENT,
        )
        cls.other_student = User.objects.create_user(
            username="otherstudent",
            password="student12345",
            email="other@shms.local",
            role=User.ROLE_STUDENT,
        )
        cls.hostel = Hostel.objects.create(name="Test Hostel", location="Block A")
        cls.room = Room.objects.create(
            hostel=cls.hostel,
            room_number="T-101",
            room_type=Room.TYPE_DOUBLE,
            capacity=2,
            available_beds=2,
        )
        cls.bed1 = Bed.objects.create(room=cls.room, bed_number="B1", is_available=True)
        cls.bed2 = Bed.objects.create(room=cls.room, bed_number="B2", is_available=True)

    def _login(self, username, password):
        client = Client()
        self.assertTrue(client.login(username=username, password=password))
        return client

    def test_home_redirects(self):
        anon = Client()
        self.assertRedirects(anon.get("/"), "/login", fetch_redirect_response=False)
        student = self._login("teststudent", "student12345")
        self.assertRedirects(student.get("/"), "/dashboard", fetch_redirect_response=False)

    def test_public_and_protected_routes(self):
        routes_anon_redirect = [
            "/dashboard",
            "/rooms",
            "/payments",
            "/book-room",
            "/bookings/history",
            "/announcements",
            "/services",
            "/complaints/",
        ]
        anon = Client()
        for path in routes_anon_redirect:
            resp = anon.get(path)
            self.assertIn(resp.status_code, (302, 403), msg=f"{path} -> {resp.status_code}")

    def test_student_cannot_access_admin_routes(self):
        student = self._login("teststudent", "student12345")
        admin_only = [
            "/analytics",
            "/rooms/add",
            "/bookings/history",
            "/bookings/export/excel/",
            "/admin-complaints/",
            "/announcements/create",
        ]
        for path in admin_only:
            resp = student.get(path)
            self.assertIn(resp.status_code, (302, 403), msg=f"{path} -> {resp.status_code}")

    def test_admin_cannot_book_room(self):
        admin = self._login("testadmin", "admin12345")
        resp = admin.get("/book-room")
        self.assertEqual(resp.status_code, 403)

    def test_student_dashboard_and_rooms(self):
        student = self._login("teststudent", "student12345")
        self.assertEqual(student.get("/dashboard").status_code, 200)
        self.assertEqual(student.get("/rooms").status_code, 200)

    def test_admin_dashboard_and_analytics(self):
        admin = self._login("testadmin", "admin12345")
        self.assertEqual(admin.get("/dashboard").status_code, 200)
        self.assertEqual(admin.get("/analytics").status_code, 200)
        self.assertEqual(admin.get("/bookings/history").status_code, 200)

    def test_booking_flow_with_email_and_notification(self):
        student = self._login("teststudent", "student12345")
        start = date.today()
        end = start + timedelta(days=90)
        mail.outbox.clear()
        before_notifications = Notification.objects.filter(recipient=self.student).count()

        resp = student.post(
            "/book-room",
            {
                "room": self.room.id,
                "bed": self.bed1.id,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
        )
        self.assertEqual(resp.status_code, 302)
        booking = Booking.objects.filter(user=self.student, bed=self.bed1).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, Booking.STATUS_BOOKED)
        self.assertTrue(booking.qr_code)

        qr_resp = student.get(f"/bookings/{booking.id}/qr")
        self.assertEqual(qr_resp.status_code, 200)

        check_in_resp = student.post(f"/check-in/{booking.id}/")
        self.assertEqual(check_in_resp.status_code, 302)
        booking.refresh_from_db()
        self.assertIsNotNone(booking.check_in_at)

        cancel_resp = student.get(f"/bookings/cancel/{booking.id}")
        self.assertEqual(cancel_resp.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CANCELLED)

        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertGreater(
            Notification.objects.filter(recipient=self.student).count(),
            before_notifications,
        )

    def test_student_cannot_view_other_booking_qr(self):
        start = date.today()
        end = start + timedelta(days=60)
        booking = Booking.objects.create(
            user=self.other_student,
            room=self.room,
            bed=self.bed2,
            start_date=start,
            end_date=end,
            status=Booking.STATUS_BOOKED,
        )
        student = self._login("teststudent", "student12345")
        resp = student.get(f"/bookings/{booking.id}/qr", follow=True)
        self.assertRedirects(resp, "/dashboard", status_code=302, target_status_code=200)

    def test_invoice_pdf_generation(self):
        paid = Payment.objects.create(
            user=self.student,
            amount=Decimal("5000.00"),
            status=Payment.STATUS_PAID,
            due_date=date.today() - timedelta(days=5),
            paid_date=timezone.now(),
        )
        student = self._login("teststudent", "student12345")
        resp = student.get(f"/receipt/{paid.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertTrue(resp.content.startswith(b"%PDF"))

        unpaid = Payment.objects.create(
            user=self.student,
            amount=Decimal("3000.00"),
            status=Payment.STATUS_UNPAID,
        )
        forbidden = student.get(f"/receipt/{unpaid.id}/")
        self.assertEqual(forbidden.status_code, 403)

    def test_complaint_and_service_uploads(self):
        student = self._login("teststudent", "student12345")
        complaint_resp = student.post(
            "/submit-complaint/",
            {"issue": "Water leak in bathroom", "image": _make_image()},
        )
        self.assertEqual(complaint_resp.status_code, 302)
        complaint = Complaint.objects.filter(user=self.student).latest("id")
        self.assertTrue(complaint.image)

        service_resp = student.post(
            "/services/request",
            {
                "request_type": ServiceRequest.TYPE_CLEANING,
                "details": "Need room cleaning",
                "attachment": _make_pdf(),
            },
        )
        self.assertEqual(service_resp.status_code, 302)
        service = ServiceRequest.objects.filter(user=self.student).latest("id")
        self.assertTrue(service.attachment)

    def test_admin_payment_update_triggers_email(self):
        payment = Payment.objects.create(
            user=self.student,
            amount=Decimal("4000.00"),
            status=Payment.STATUS_UNPAID,
            due_date=date.today() + timedelta(days=7),
        )
        admin = self._login("testadmin", "admin12345")
        mail.outbox.clear()
        resp = admin.post(
            f"/payments/update/{payment.id}",
            {
                "amount": "4000.00",
                "status": Payment.STATUS_PAID,
                "due_date": payment.due_date.isoformat(),
                "paid_date": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertGreaterEqual(len(mail.outbox), 1)

    def test_admin_complaint_status_email(self):
        complaint = Complaint.objects.create(user=self.student, issue="Broken window")
        admin = self._login("testadmin", "admin12345")
        mail.outbox.clear()
        resp = admin.post(
            "/admin-complaints/",
            {"complaint_id": complaint.id, "status": Complaint.STATUS_IN_PROGRESS},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertGreaterEqual(len(mail.outbox), 1)

    def test_announcement_create_emails_students(self):
        admin = self._login("testadmin", "admin12345")
        mail.outbox.clear()
        resp = admin.post(
            "/announcements/create",
            {"title": "Test Notice", "message": "Hostel maintenance tomorrow."},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertGreater(len(mail.outbox), 0)

    def test_admin_export_bookings_excel(self):
        admin = self._login("testadmin", "admin12345")
        resp = admin.get("/bookings/export/excel/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("spreadsheetml", resp["Content-Type"])

    def test_jwt_api_auth_and_endpoints(self):
        client = Client()
        token_resp = client.post(
            "/api/token/",
            data=json.dumps({"username": "teststudent", "password": "student12345"}),
            content_type="application/json",
        )
        self.assertEqual(token_resp.status_code, 200)
        tokens = token_resp.json()
        self.assertIn("access", tokens)
        auth = {"HTTP_AUTHORIZATION": f"Bearer {tokens['access']}"}

        for endpoint in ["/api/rooms/", "/api/bookings/", "/api/payments/", "/api/announcements/", "/api/services/", "/api/complaints/"]:
            resp = client.get(endpoint, **auth)
            self.assertEqual(resp.status_code, 200, msg=endpoint)

        refresh_resp = client.post(
            "/api/token/refresh/",
            data=json.dumps({"refresh": tokens["refresh"]}),
            content_type="application/json",
        )
        self.assertEqual(refresh_resp.status_code, 200)

    def test_api_booking_create(self):
        available_bed = Bed.objects.create(room=self.room, bed_number="B9", is_available=True)
        Room.objects.filter(pk=self.room.pk).update(available_beds=1)
        client = Client()
        token = client.post(
            "/api/token/",
            data=json.dumps({"username": "teststudent", "password": "student12345"}),
            content_type="application/json",
        ).json()["access"]
        start = (date.today() + timedelta(days=10)).isoformat()
        end = (date.today() + timedelta(days=100)).isoformat()
        resp = client.post(
            "/api/bookings/",
            data=json.dumps({"room": self.room.id, "bed": available_bed.id, "start_date": start, "end_date": end, "status": "booked"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertIn(resp.status_code, (200, 201), msg=resp.content)

    def test_api_student_cannot_create_announcement(self):
        client = Client()
        token = client.post(
            "/api/token/",
            data=json.dumps({"username": "teststudent", "password": "student12345"}),
            content_type="application/json",
        ).json()["access"]
        resp = client.post(
            "/api/announcements/",
            data=json.dumps({"title": "Hack", "message": "Should fail"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(resp.status_code, 403)

    @override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
    def test_websocket_notification_delivery(self):
        async def run_ws_flow():
            communicator = WebsocketCommunicator(application, "/ws/notifications/")
            communicator.scope["user"] = self.student
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                f"user_{self.student.id}",
                {
                    "type": "notification.message",
                    "payload": {
                        "id": 99,
                        "title": "WS Test",
                        "message": "Realtime ping",
                        "notification_type": "info",
                        "related_url": "",
                        "created_at": timezone.now().isoformat(),
                    },
                },
            )
            response = await communicator.receive_json_from(timeout=2)
            await communicator.disconnect()
            return response

        response = async_to_sync(run_ws_flow)()
        self.assertEqual(response["title"], "WS Test")

    def test_create_notification_persists_and_broadcasts(self):
        with override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}):
            before = Notification.objects.filter(recipient=self.student).count()
            notification = create_notification(
                recipient=self.student,
                title="Persisted",
                message="Stored in DB",
            )
            self.assertEqual(Notification.objects.filter(recipient=self.student).count(), before + 1)
            self.assertEqual(notification.title, "Persisted")

    def test_websocket_rejects_anonymous(self):
        communicator = WebsocketCommunicator(application, "/ws/notifications/")
        connected, _ = async_to_sync(communicator.connect)()
        self.assertFalse(connected)

    def test_register_and_logout(self):
        anon = Client()
        resp = anon.post(
            "/register",
            {
                "username": "newstudent",
                "email": "newstudent@shms.local",
                "first_name": "New",
                "last_name": "Student",
                "password1": "securepass123",
                "password2": "securepass123",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="newstudent").exists())

        client = self._login("newstudent", "securepass123")
        logout_resp = client.get("/logout")
        self.assertEqual(logout_resp.status_code, 302)
