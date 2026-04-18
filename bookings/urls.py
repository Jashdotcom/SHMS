from django.urls import path

from .views import book_room_view, booking_history_view, cancel_booking_view

app_name = "bookings"

urlpatterns = [
    path("book-room", book_room_view, name="book_room"),
    path("bookings/history", booking_history_view, name="history"),
    path("bookings/cancel/<int:booking_id>", cancel_booking_view, name="cancel"),
]
