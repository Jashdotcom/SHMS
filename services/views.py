from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User

from .forms import ComplaintForm, ServiceRequestForm
from .models import Complaint, ServiceRequest


def _is_admin_user(user):
	return user.is_authenticated and (user.is_staff or user.role == User.ROLE_ADMIN)


@login_required
def complaints_list_view(request):
	complaints = Complaint.objects.select_related("user")

	if request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		complaints = complaints.filter(user=request.user)

	return render(request, "services/complaints.html", {"complaints": complaints})


@user_passes_test(_is_admin_user)
def admin_complaints_view(request):
	complaints = Complaint.objects.select_related("user").all()

	if request.method == "POST":
		complaint_id = request.POST.get("complaint_id")
		status = request.POST.get("status")
		complaint = get_object_or_404(Complaint, pk=complaint_id)

		if status in [choice[0] for choice in Complaint.STATUS_CHOICES]:
			complaint.status = status
			complaint.save()
			messages.success(request, f"Complaint status updated to {complaint.get_status_display()}.")

	return render(request, "services/admin_complaints.html", {"complaints": complaints})


@login_required
def services_view(request):
	requests = ServiceRequest.objects.select_related("user")

	if request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		requests = requests.filter(user=request.user)

	return render(request, "services/services.html", {"service_requests": requests})


@login_required
def submit_complaint_view(request):
	if request.method == "POST":
		form = ComplaintForm(request.POST, request.FILES)
		if form.is_valid():
			complaint = form.save(commit=False)
			complaint.user = request.user
			complaint.save()
			messages.success(request, "Complaint submitted successfully with proof image.")
			return redirect("services:complaints")
	else:
		form = ComplaintForm()

	return render(request, "services/submit_complaint.html", {"form": form})


@login_required
def request_service_view(request):
	if request.method == "POST":
		form = ServiceRequestForm(request.POST)
		if form.is_valid():
			service_request = form.save(commit=False)
			service_request.user = request.user
			service_request.save()
			messages.success(request, "Service request submitted successfully.")
			return redirect("services:list")
	else:
		form = ServiceRequestForm()

	return render(request, "services/request_service.html", {"form": form})
