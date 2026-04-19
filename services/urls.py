from django.urls import path

from .views import (
    admin_complaints_view,
    complaints_list_view,
    request_service_view,
    services_view,
    submit_complaint_view,
    update_service_status,
)

app_name = "services"

urlpatterns = [
    path("services", services_view, name="list"),
    path("complaints/", complaints_list_view, name="complaints"),
    path("submit-complaint/", submit_complaint_view, name="complaint"),
    path("admin-complaints/", admin_complaints_view, name="admin_complaints"),
    path("services/request", request_service_view, name="request"),
    path("services/update/<int:id>/", update_service_status, name="update_service_status"),
]
