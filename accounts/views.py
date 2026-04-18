from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import redirect, render

from bookings.models import Booking
from hostel.models import Bed
from payments.models import Payment

from .forms import LoginForm, RegisterForm
from .models import User


class UserLoginView(LoginView):
	template_name = "accounts/login.html"
	form_class = LoginForm
	redirect_authenticated_user = True

	def get_success_url(self):
		return self.request.GET.get("next") or self.request.POST.get("next") or "/dashboard"


def register_view(request):
	if request.user.is_authenticated:
		return redirect("accounts:dashboard")

	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful.")
			return redirect("accounts:dashboard")
	else:
		form = RegisterForm()

	return render(request, "accounts/register.html", {"form": form})


@login_required
def logout_view(request):
	logout(request)
	messages.info(request, "You have been logged out.")
	return redirect("accounts:login")


@login_required
def dashboard_view(request):
	total_students = User.objects.filter(role=User.ROLE_STUDENT).count()
	rooms_booked = Booking.objects.filter(status=Booking.STATUS_BOOKED).values("room").distinct().count()
	available_beds = Bed.objects.filter(is_available=True).count()

	payment_summary = Payment.objects.aggregate(
		paid=Count("id", filter=Q(status=Payment.STATUS_PAID)),
		partial=Count("id", filter=Q(status=Payment.STATUS_PARTIAL)),
		unpaid=Count("id", filter=Q(status=Payment.STATUS_UNPAID)),
	)

	# Revenue chart uses collected payments only (status=paid), grouped by month.
	revenue_by_month = (
		Payment.objects.filter(status=Payment.STATUS_PAID)
		.annotate(month=TruncMonth("date"))
		.values("month")
		.annotate(total=Sum("amount"))
		.order_by("month")
	)

	revenue_chart_labels = [
		entry["month"].strftime("%b %Y")
		for entry in revenue_by_month
		if entry["month"] is not None
	]
	revenue_chart_values = [
		float(entry["total"] or 0)
		for entry in revenue_by_month
		if entry["month"] is not None
	]

	recent_bookings = Booking.objects.select_related("user", "room", "bed").order_by("-created_at")[:6]

	context = {
		"total_students": total_students,
		"rooms_booked": rooms_booked,
		"available_beds": available_beds,
		"payment_summary": payment_summary,
		"recent_bookings": recent_bookings,
		"chart_labels": ["Paid", "Partial", "Unpaid"],
		"chart_values": [
			payment_summary["paid"] or 0,
			payment_summary["partial"] or 0,
			payment_summary["unpaid"] or 0,
		],
		"revenue_chart_labels": revenue_chart_labels,
		"revenue_chart_values": revenue_chart_values,
	}
	return render(request, "dashboard.html", context)
