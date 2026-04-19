from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from reportlab.pdfgen import canvas

from accounts.models import User

from .forms import PaymentUpdateForm
from .models import Payment


def _is_admin_user(user):
	return user.is_authenticated and (user.is_staff or user.role == User.ROLE_ADMIN)


@login_required
def payment_list_view(request):
	payments = Payment.objects.select_related("user")
	is_admin = request.user.role == User.ROLE_ADMIN or request.user.is_staff or request.user.is_superuser
	if request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		payments = payments.filter(user=request.user)
	return render(request, "payments/payments.html", {"payments": payments, "is_admin": is_admin})


@user_passes_test(_is_admin_user)
def payment_update_view(request, payment_id):
	payment = get_object_or_404(Payment, pk=payment_id)

	if request.method == "POST":
		form = PaymentUpdateForm(request.POST, instance=payment)
		if form.is_valid():
			form.save()
			messages.success(request, "Payment updated successfully.")
			return redirect("payments:list")
	else:
		form = PaymentUpdateForm(instance=payment)

	return render(request, "payments/update_payment.html", {"form": form, "payment": payment})


@login_required
def download_receipt(request, payment_id):
	payment = get_object_or_404(Payment.objects.select_related("user"), pk=payment_id)
	is_admin = request.user.role == User.ROLE_ADMIN or request.user.is_staff or request.user.is_superuser

	if not is_admin and payment.user != request.user:
		return HttpResponseForbidden("You are not allowed to download this receipt.")

	if payment.status != Payment.STATUS_PAID:
		return HttpResponseForbidden("Receipt is only available for paid payments.")

	response = HttpResponse(content_type="application/pdf")
	response["Content-Disposition"] = f'attachment; filename="receipt_{payment.id}.pdf"'

	pdf = canvas.Canvas(response)
	pdf.setFont("Helvetica-Bold", 16)
	pdf.drawString(100, 800, "Smart Hostel Receipt")
	pdf.setFont("Helvetica", 12)
	pdf.drawString(100, 770, f"Receipt No: RCP-{payment.id:05d}")
	pdf.drawString(100, 750, f"Student: {payment.user.username}")
	pdf.drawString(100, 730, f"Amount Paid: ₹{payment.get_total_amount()}")
	pdf.drawString(100, 710, f"Paid Date: {payment.paid_date.date() if payment.paid_date else '-'}")
	pdf.drawString(100, 690, f"Status: {payment.get_status_display()}")
	pdf.drawString(100, 660, "Thank you for your payment!")
	pdf.drawString(100, 620, "Authorized Signature: ____________________")
	pdf.showPage()
	pdf.save()
	return response
