from django.urls import path

from .views import (
    book_room_view,
    booking_history_view,
    booking_qr_view,
    cancel_booking_view,
    check_in_view,
    get_beds,
)

app_name = "bookings"

urlpatterns = [
    path("book-room", book_room_view, name="book_room"),
    path("get-beds/", get_beds, name="get_beds"),
    path("check-in/<int:booking_id>/", check_in_view, name="check_in"),
    path("bookings/<int:booking_id>/qr", booking_qr_view, name="qr"),
    path("bookings/history", booking_history_view, name="history"),
    path("bookings/cancel/<int:booking_id>", cancel_booking_view, name="cancel"),
]
