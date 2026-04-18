from django.urls import path

from .views import UserLoginView, dashboard_view, logout_view, register_view

app_name = "accounts"

urlpatterns = [
    path("login", UserLoginView.as_view(), name="login"),
    path("register", register_view, name="register"),
    path("logout", logout_view, name="logout"),
    path("dashboard", dashboard_view, name="dashboard"),
]
