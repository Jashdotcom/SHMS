from rest_framework import serializers

from announcements.models import Announcement
from bookings.models import Booking
from hostel.models import Room
from payments.models import Payment
from services.models import Complaint, ServiceRequest


class RoomSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)

    class Meta:
        model = Room
        fields = ["id", "hostel", "hostel_name", "room_number", "room_type", "capacity", "available_beds"]


class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    bed_number = serializers.CharField(source="bed.bed_number", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "user", "user_name", "room", "room_number", "bed", "bed_number", "start_date", "end_date", "expires_at", "status", "created_at"]
        read_only_fields = ["user", "created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ["id", "user", "user_name", "invoice_number", "invoice_generated_at", "amount", "status", "due_date", "paid_date", "late_fee", "total_amount", "date", "updated_at"]
        read_only_fields = ["user", "invoice_number", "invoice_generated_at", "late_fee", "date", "updated_at"]

    def get_total_amount(self, obj):
        return obj.get_total_amount()


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Announcement
        fields = ["id", "title", "message", "created_at", "created_by", "created_by_name"]
        read_only_fields = ["created_by", "created_at"]


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ["id", "issue", "image", "attachment", "status", "created_at", "updated_at"]
        read_only_fields = ["status", "created_at", "updated_at"]


class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = ["id", "request_type", "details", "attachment", "status", "created_at", "updated_at"]
        read_only_fields = ["status", "created_at", "updated_at"]