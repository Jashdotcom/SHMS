from django.urls import path

from .views import payment_list_view, payment_update_view

app_name = "payments"

urlpatterns = [
    path("payments", payment_list_view, name="list"),
    path("payments/update/<int:payment_id>", payment_update_view, name="update"),
]
