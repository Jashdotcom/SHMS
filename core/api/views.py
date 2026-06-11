from rest_framework import permissions, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from announcements.models import Announcement
from bookings.models import Booking
from hostel.models import Room
from payments.models import Payment
from services.models import Complaint, ServiceRequest

from .serializers import (
    AnnouncementSerializer,
    BookingSerializer,
    ComplaintSerializer,
    PaymentSerializer,
    RoomSerializer,
    ServiceRequestSerializer,
)
from ..permissions import IsAdminOrAuthenticatedReadOnly, IsAdminOrReadOwnData


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Room.objects.select_related("hostel").all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAdminOrReadOwnData]

    def get_queryset(self):
        queryset = Booking.objects.select_related("user", "room", "bed", "room__hostel")
        user = self.request.user
        if user.is_staff or getattr(user, "role", None) == "admin":
            return queryset
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrReadOwnData]

    def get_queryset(self):
        queryset = Payment.objects.select_related("user")
        user = self.request.user
        if user.is_staff or getattr(user, "role", None) == "admin":
            return queryset
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAdminOrAuthenticatedReadOnly]

    def get_queryset(self):
        return Announcement.objects.select_related("created_by")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceRequestSerializer
    permission_classes = [IsAdminOrReadOwnData]

    def get_queryset(self):
        queryset = ServiceRequest.objects.select_related("user")
        user = self.request.user
        if user.is_staff or getattr(user, "role", None) == "admin":
            return queryset
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAdminOrReadOwnData]

    def get_queryset(self):
        queryset = Complaint.objects.select_related("user")
        user = self.request.user
        if user.is_staff or getattr(user, "role", None) == "admin":
            return queryset
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AuthTokenView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class AuthTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]