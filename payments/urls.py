from django.urls import path

from .views import download_receipt, payment_list_view, payment_update_view

app_name = "payments"

urlpatterns = [
    path("payments", payment_list_view, name="list"),
    path("receipt/<int:payment_id>/", download_receipt, name="download_receipt"),
    path("payments/update/<int:payment_id>", payment_update_view, name="update"),
]
