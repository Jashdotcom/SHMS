from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnnouncementViewSet,
    AuthTokenRefreshView,
    AuthTokenView,
    BookingViewSet,
    ComplaintViewSet,
    PaymentViewSet,
    RoomViewSet,
    ServiceViewSet,
)

router = DefaultRouter()
router.register(r"bookings", BookingViewSet, basename="bookings")
router.register(r"rooms", RoomViewSet, basename="rooms")
router.register(r"payments", PaymentViewSet, basename="payments")
router.register(r"announcements", AnnouncementViewSet, basename="announcements")
router.register(r"services", ServiceViewSet, basename="services")
router.register(r"complaints", ComplaintViewSet, basename="complaints")

urlpatterns = [
    path("token/", AuthTokenView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", AuthTokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]