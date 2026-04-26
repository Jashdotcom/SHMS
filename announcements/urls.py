from django.urls import path

from .views import (
    announcement_create_view,
    announcement_delete_view,
    announcement_list_view,
    announcement_update_view,
)

app_name = "announcements"

urlpatterns = [
    path("announcements", announcement_list_view, name="list"),
    path("announcements/create", announcement_create_view, name="create"),
    path("announcements/<int:announcement_id>/edit", announcement_update_view, name="update"),
    path("announcements/<int:announcement_id>/delete", announcement_delete_view, name="delete"),
]
