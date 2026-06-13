from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date

from announcements.models import Announcement
from bookings.models import Booking
from hostel.models import Room
from payments.models import Payment
from services.models import Complaint

from .forms import LoginForm, RegisterForm
from .models import User


def _is_admin_user(user):
	role = (getattr(user, "role", "") or "").strip().lower()
	return bool(user and user.is_authenticated and (user.is_superuser or role == User.ROLE_ADMIN.lower()))


class UserLoginView(LoginView):
	template_name = "accounts/login.html"
	form_class = LoginForm
	redirect_authenticated_user = True

	def get_success_url(self):
		return self.request.GET.get("next") or self.request.POST.get("next") or "/dashboard"

	def form_valid(self, form):
		response = super().form_valid(form)
		storage = get_messages(self.request)
		for _ in storage:
			pass
		messages.success(self.request, f"Welcome {self.request.user.first_name}")
		return response


def register_view(request):
	if request.user.is_authenticated:
		return redirect("accounts:dashboard")

	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			try:
				user = form.save(commit=True)
				user.save()
				messages.success(request, "Registration successful! Please log in.")
				return redirect("accounts:login")
			except Exception as e:
				messages.error(request, f"An error occurred during registration: {str(e)}")
				form = RegisterForm()
		else:
			# Form has errors - they will be displayed in template
			pass
	else:
		form = RegisterForm()

	return render(request, "accounts/register.html", {"form": form})


@login_required
def logout_view(request):
	logout(request)
	messages.info(request, "You have been logged out.")
	return redirect("accounts:login")


def _build_dashboard_context(request):
	is_admin = _is_admin_user(request.user)
	start_date = parse_date(request.GET.get("start_date") or "")
	end_date = parse_date(request.GET.get("end_date") or "")

	def apply_date_filter(queryset, field_name="created_at__date"):
		if start_date:
			queryset = queryset.filter(**{f"{field_name}__gte": start_date})
		if end_date:
			queryset = queryset.filter(**{f"{field_name}__lte": end_date})
		return queryset

	total_students = User.objects.filter(role=User.ROLE_STUDENT).count()
	rooms_booked = Booking.objects.filter(status=Booking.STATUS_BOOKED).values("room").distinct().count()
	available_beds = Room.objects.aggregate(total=Sum("available_beds"))["total"] or 0
	total_capacity = Room.objects.aggregate(total=Sum("capacity"))["total"] or 0
	active_bookings = Booking.objects.filter(status=Booking.STATUS_BOOKED).count()
	occupancy_percentage = round((active_bookings / total_capacity) * 100, 1) if total_capacity else 0
	latest_announcements = Announcement.objects.select_related("created_by").all()[:5]
	filtered_bookings = apply_date_filter(Booking.objects.select_related("user", "room", "bed"), "created_at__date")
	filtered_payments = apply_date_filter(Payment.objects.all(), "date__date")
	filtered_complaints = apply_date_filter(Complaint.objects.all(), "created_at__date")
	total_bookings = filtered_bookings.count()

	payment_summary = filtered_payments.aggregate(
		paid=Count("id", filter=Q(status=Payment.STATUS_PAID)),
		partial=Count("id", filter=Q(status=Payment.STATUS_PARTIAL)),
		unpaid=Count("id", filter=Q(status=Payment.STATUS_UNPAID)),
	)
	complaint_summary = filtered_complaints.aggregate(
		pending=Count("id", filter=Q(status=Complaint.STATUS_PENDING)),
		in_progress=Count("id", filter=Q(status=Complaint.STATUS_IN_PROGRESS)),
		resolved=Count("id", filter=Q(status=Complaint.STATUS_RESOLVED)),
	)

	bookings_trend_labels = []
	bookings_trend_values = []
	payment_trend_labels = []
	payment_trend_values = []
	if is_admin:
		bookings_by_month = (
			filtered_bookings
			.annotate(month=TruncMonth("created_at"))
			.values("month")
			.annotate(total=Count("id"))
			.order_by("month")
		)
		bookings_trend_labels = [entry["month"].strftime("%b %Y") for entry in bookings_by_month if entry["month"]]
		bookings_trend_values = [entry["total"] for entry in bookings_by_month if entry["month"]]

		payment_by_month = (
			filtered_payments.filter(status=Payment.STATUS_PAID)
			.annotate(month=TruncMonth("date"))
			.values("month")
			.annotate(total=Sum("amount"))
			.order_by("month")
		)
		payment_trend_labels = [entry["month"].strftime("%b %Y") for entry in payment_by_month if entry["month"]]
		payment_trend_values = [float(entry["total"] or 0) for entry in payment_by_month if entry["month"]]

	recent_bookings = filtered_bookings.order_by("-created_at")[:6]

	context = {
		"total_students": total_students,
		"rooms_booked": rooms_booked,
		"available_beds": available_beds,
		"total_capacity": total_capacity,
		"active_bookings": active_bookings,
		"occupancy_percentage": occupancy_percentage,
		"total_bookings": total_bookings,
		"payment_summary": payment_summary,
		"complaint_summary": complaint_summary,
		"recent_bookings": recent_bookings,
		"latest_announcements": latest_announcements,
		"payment_chart_labels": ["Paid", "Partial", "Unpaid"],
		"payment_chart_values": [
			payment_summary["paid"] or 0,
			payment_summary["partial"] or 0,
			payment_summary["unpaid"] or 0,
		],
		"bookings_trend_labels": bookings_trend_labels,
		"bookings_trend_values": bookings_trend_values,
		"payment_trend_labels": payment_trend_labels,
		"payment_trend_values": payment_trend_values,
		"start_date": start_date.isoformat() if start_date else "",
		"end_date": end_date.isoformat() if end_date else "",
	}
	if is_admin:
		context["monthly_bookings_labels"] = bookings_trend_labels
		context["monthly_bookings_values"] = bookings_trend_values
		context["monthly_payments_labels"] = payment_trend_labels
		context["monthly_payments_values"] = payment_trend_values
	return context


@login_required
def dashboard_view(request):
	return render(request, "dashboard.html", _build_dashboard_context(request))


@login_required
def analytics_view(request):
	if not _is_admin_user(request.user):
		return redirect("accounts:dashboard")
	return render(request, "dashboard.html", _build_dashboard_context(request))
