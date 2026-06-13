from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.utils.dateparse import parse_date

from accounts.models import User
from core.emails import send_templated_email
from core.notifications import create_notification

from .forms import ComplaintForm, ServiceRequestForm
from .models import Complaint, ServiceRequest


def _is_admin_user(user):
	return user.is_authenticated and (user.is_staff or user.role == User.ROLE_ADMIN)


@login_required
def complaints_list_view(request):
	complaints = Complaint.objects.select_related("user")

	if request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		complaints = complaints.filter(user=request.user)

	status_query = request.GET.get("status") or ""
	if status_query:
		complaints = complaints.filter(status=status_query)
	status_summary = {
		"pending": complaints.filter(status=Complaint.STATUS_PENDING).count(),
		"in_progress": complaints.filter(status=Complaint.STATUS_IN_PROGRESS).count(),
		"resolved": complaints.filter(status=Complaint.STATUS_RESOLVED).count(),
	}

	paginator = Paginator(complaints.order_by("-created_at"), 8)
	page_number = request.GET.get("page")
	complaint_page = paginator.get_page(page_number)

	return render(request, "services/complaints.html", {"complaints": complaint_page, "status_query": status_query, "status_summary": status_summary})


@user_passes_test(_is_admin_user)
def admin_complaints_view(request):
	complaints = Complaint.objects.select_related("user").all()
	search_query = request.GET.get("search") or ""
	status_query = request.GET.get("status") or ""
	created_from = parse_date(request.GET.get("created_from") or "")
	created_to = parse_date(request.GET.get("created_to") or "")

	if search_query:
		complaints = complaints.filter(issue__icontains=search_query)
	if status_query:
		complaints = complaints.filter(status=status_query)
	if created_from:
		complaints = complaints.filter(created_at__date__gte=created_from)
	if created_to:
		complaints = complaints.filter(created_at__date__lte=created_to)

	if request.method == "POST":
		complaint_id = request.POST.get("complaint_id")
		status = request.POST.get("status")
		complaint = get_object_or_404(Complaint, pk=complaint_id)

		if status in [choice[0] for choice in Complaint.STATUS_CHOICES]:
			previous_status = complaint.status
			complaint.status = status
			complaint.save()
			messages.success(request, f"Complaint status updated to {complaint.get_status_display()}.")
			if previous_status != complaint.status:
				message = f"Your complaint status has been updated to {complaint.get_status_display()}."
				if complaint.user.email:
					send_templated_email(
						subject="Complaint Status Update | SHMS",
						template_name="emails/notification.html",
						context={
							"title": "Complaint status updated",
							"message": message,
							"action_url": "",
						},
						recipients=[complaint.user.email],
					)
				create_notification(
					recipient=complaint.user,
					title="Complaint status updated",
					message=message,
				)
			return redirect("services:admin_complaints")

	paginator = Paginator(complaints.order_by("-created_at"), 10)
	complaint_page = paginator.get_page(request.GET.get("page"))

	return render(
		request,
		"services/admin_complaints.html",
		{
			"complaints": complaint_page,
			"search_query": search_query,
			"status_query": status_query,
			"created_from": created_from.isoformat() if created_from else "",
			"created_to": created_to.isoformat() if created_to else "",
		},
	)


@login_required
def services_view(request):
	requests = ServiceRequest.objects.select_related("user")

	if request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		requests = requests.filter(user=request.user)

	search_query = request.GET.get("search") or ""
	status_query = request.GET.get("status") or ""
	if search_query:
		requests = requests.filter(details__icontains=search_query)
	if status_query:
		requests = requests.filter(status=status_query)

	paginator = Paginator(requests.order_by("-created_at"), 10)
	request_page = paginator.get_page(request.GET.get("page"))

	return render(
		request,
		"services/services.html",
		{"service_requests": request_page, "search_query": search_query, "status_query": status_query},
	)


@login_required
def submit_complaint_view(request):
	if request.method == "POST":
		form = ComplaintForm(request.POST, request.FILES)
		if form.is_valid():
			complaint = form.save(commit=False)
			complaint.user = request.user
			complaint.save()
			create_notification(
				recipient=request.user,
				title="Complaint submitted",
				message="Your complaint has been received and is now under review.",
			)
			messages.success(request, "Complaint submitted successfully with proof image.")
			return redirect("services:complaints")
	else:
		form = ComplaintForm()

	return render(request, "services/submit_complaint.html", {"form": form})


@login_required
def request_service_view(request):
	if request.method == "POST":
		form = ServiceRequestForm(request.POST, request.FILES)
		if form.is_valid():
			service_request = form.save(commit=False)
			service_request.user = request.user
			service_request.save()
			create_notification(
				recipient=request.user,
				title="Service request submitted",
				message="Your service request has been created successfully.",
			)
			messages.success(request, "Service request submitted successfully.")
			return redirect("services:list")
	else:
		form = ServiceRequestForm()

	return render(request, "services/request_service.html", {"form": form})


@user_passes_test(_is_admin_user)
def update_service_status(request, id):
	service = get_object_or_404(ServiceRequest, id=id)

	if request.method == "POST":
		new_status = request.POST.get("status")
		allowed_statuses = [choice[0] for choice in ServiceRequest.STATUS_CHOICES]
		if new_status in allowed_statuses:
			service.status = new_status
			service.save(update_fields=["status"])

			if service.user.email:
				message = (
					f"Your service request '{service.get_request_type_display()}' has been updated to "
					f"{service.get_status_display()}."
				)
				send_templated_email(
					subject="Service Request Update | SHMS",
					template_name="emails/notification.html",
					context={"title": "Service request updated", "message": message, "action_url": ""},
					recipients=[service.user.email],
				)
				create_notification(recipient=service.user, title="Service request updated", message=message)
				messages.success(request, "Status updated and email sent.")
			else:
				messages.warning(request, "Status updated, but student email is not available.")

			return redirect("services:list")
		messages.error(request, "Invalid status selected.")

	return render(request, "services/update_status.html", {"service": service})
