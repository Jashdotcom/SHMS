from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import User

from .forms import ComplaintForm, ServiceRequestForm
from .models import Complaint, ServiceRequest


@login_required
def services_view(request):
	complaints = Complaint.objects.select_related("user")
	requests = ServiceRequest.objects.select_related("user")

	if request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		complaints = complaints.filter(user=request.user)
		requests = requests.filter(user=request.user)

	context = {
		"complaints": complaints,
		"service_requests": requests,
	}
	return render(request, "services/services.html", context)


@login_required
def submit_complaint_view(request):
	if request.method == "POST":
		form = ComplaintForm(request.POST)
		if form.is_valid():
			complaint = form.save(commit=False)
			complaint.user = request.user
			complaint.save()
			messages.success(request, "Complaint submitted successfully.")
			return redirect("services:list")
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
