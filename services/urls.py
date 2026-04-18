from django.urls import path

from .views import request_service_view, services_view, submit_complaint_view

app_name = "services"

urlpatterns = [
    path("services", services_view, name="list"),
    path("services/complaint", submit_complaint_view, name="complaint"),
    path("services/request", request_service_view, name="request"),
]
