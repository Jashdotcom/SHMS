from django.urls import path

from .views import add_room_view, room_list_view

app_name = "hostel"

urlpatterns = [
    path("rooms", room_list_view, name="rooms"),
    path("rooms/add", add_room_view, name="add_room"),
]
