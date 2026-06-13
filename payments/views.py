import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from accounts.models import User
from core.emails import send_templated_email
from core.notifications import create_notification

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
	status_query = request.GET.get("status") or ""
	student_query = request.GET.get("student") or ""
	due_from = parse_date(request.GET.get("due_from") or "")
	due_to = parse_date(request.GET.get("due_to") or "")

	if status_query:
		payments = payments.filter(status=status_query)
	if student_query and is_admin:
		payments = payments.filter(user__username__icontains=student_query)
	if due_from:
		payments = payments.filter(due_date__gte=due_from)
	if due_to:
		payments = payments.filter(due_date__lte=due_to)

	paginator = Paginator(payments.order_by("-date"), 10)
	page_number = request.GET.get("page")
	payment_page = paginator.get_page(page_number)

	return render(
		request,
		"payments/payments.html",
		{
			"payments": payment_page,
			"is_admin": is_admin,
			"status_query": status_query,
			"student_query": student_query,
			"due_from": due_from.isoformat() if due_from else "",
			"due_to": due_to.isoformat() if due_to else "",
		},
	)


@user_passes_test(_is_admin_user)
def payment_update_view(request, payment_id):
	payment = get_object_or_404(Payment, pk=payment_id)
	previous_status = payment.status

	if request.method == "POST":
		form = PaymentUpdateForm(request.POST, instance=payment)
		if form.is_valid():
			updated_payment = form.save()
			if updated_payment.status != previous_status:
				status_label = updated_payment.get_status_display()
				if updated_payment.user.email:
					send_templated_email(
						subject="Payment Status Updated | SHMS",
						template_name="emails/notification.html",
						context={
							"title": "Payment status updated",
							"message": f"Your payment of Rs. {updated_payment.amount} is now marked as {status_label}.",
							"action_url": request.build_absolute_uri(reverse("payments:download_receipt", args=[updated_payment.id])),
						},
						recipients=[updated_payment.user.email],
					)
				create_notification(
					recipient=updated_payment.user,
					title="Payment status updated",
					message=f"Your payment has been updated to {status_label}.",
					related_url=reverse("payments:download_receipt", args=[updated_payment.id]),
				)
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

	currency_prefix = "Rs. "
	amount_font_name = "Helvetica"
	unicode_font_name = "ReceiptUnicode"
	font_candidates = [
		os.path.join(settings.BASE_DIR, "static", "fonts", "Arial.ttf"),
		"C:/Windows/Fonts/arial.ttf",
		"C:/Windows/Fonts/seguiemj.ttf",
		"C:/Windows/Fonts/segoeui.ttf",
	]
	for font_path in font_candidates:
		if os.path.exists(font_path):
			if unicode_font_name not in pdfmetrics.getRegisteredFontNames():
				pdfmetrics.registerFont(TTFont(unicode_font_name, font_path))
			amount_font_name = unicode_font_name
			currency_prefix = "₹"
			break

	pdf = canvas.Canvas(response, pagesize=letter)
	width, height = letter
	left_margin = 0.85 * inch
	right_margin = width - 0.85 * inch
	top_y = height - 0.85 * inch
	logo_path = os.path.join(settings.BASE_DIR, "static", "img", "shms_logo.png")

	# Header block
	if os.path.exists(logo_path):
		pdf.drawImage(logo_path, left_margin, top_y - 30, width=32, height=32, preserveAspectRatio=True, mask="auto")
	else:
		pdf.setFillColor(colors.HexColor("#0d6efd"))
		pdf.circle(left_margin + 18, top_y - 6, 16, fill=1, stroke=0)
		pdf.setFillColor(colors.white)
		pdf.setFont("Helvetica-Bold", 10)
		pdf.drawCentredString(left_margin + 18, top_y - 10, "SHMS")

	pdf.setFillColor(colors.black)
	pdf.setFont("Helvetica-Bold", 18)
	pdf.drawString(left_margin + 42, top_y - 4, "Smart Hostel Management System")
	pdf.setFont("Helvetica", 11)
	pdf.setFillColor(colors.HexColor("#555555"))
	pdf.drawString(left_margin + 42, top_y - 20, "Payment Receipt")

	pdf.setStrokeColor(colors.HexColor("#0d6efd"))
	pdf.setLineWidth(1.2)
	pdf.line(left_margin, top_y - 34, right_margin, top_y - 34)

	# Receipt summary
	pdf.setFillColor(colors.black)
	pdf.setFont("Helvetica-Bold", 12)
	pdf.drawString(left_margin, top_y - 58, f"Invoice No: {payment.invoice_number or f'INV-{payment.id:05d}'}")
	pdf.setFont("Helvetica", 11)
	pdf.drawString(left_margin, top_y - 82, f"Student: {payment.user.username}")
	pdf.drawString(left_margin, top_y - 104, f"Generated At: {payment.invoice_generated_at.strftime('%d %b %Y, %I:%M %p') if payment.invoice_generated_at else payment.date.strftime('%d %b %Y, %I:%M %p')}")
	pdf.drawString(left_margin, top_y - 126, f"Payment Date: {payment.paid_date.date() if payment.paid_date else '-'}")
	pdf.drawString(left_margin, top_y - 148, f"Due Date: {payment.due_date or '-'}")
	pdf.drawString(left_margin, top_y - 170, f"Status: {payment.get_status_display()}")

	# Amount box
	box_top = top_y - 218
	box_height = 98
	pdf.setStrokeColor(colors.HexColor("#0d6efd"))
	pdf.setFillColor(colors.HexColor("#eef5ff"))
	pdf.roundRect(left_margin, box_top - box_height, right_margin - left_margin, box_height, 10, stroke=1, fill=1)
	pdf.setFillColor(colors.black)
	pdf.setFont(amount_font_name, 11)
	pdf.drawString(left_margin + 16, box_top - 22, f"Base Amount: {currency_prefix}{payment.amount}")
	pdf.drawString(left_margin + 16, box_top - 42, f"Late Fee: {currency_prefix}{payment.late_fee}")
	pdf.drawString(left_margin + 16, box_top - 62, f"Tax/Extras: {currency_prefix}0.00")
	pdf.setFont(amount_font_name, 13)
	pdf.drawString(left_margin + 16, box_top - 82, f"Invoice Total: {currency_prefix}{payment.get_total_amount()}")

	# Footer note
	pdf.setFillColor(colors.HexColor("#444444"))
	pdf.setFont("Helvetica", 11)
	pdf.drawString(left_margin, 150, "Thank you for keeping your hostel account up to date.")
	pdf.setStrokeColor(colors.HexColor("#cccccc"))
	pdf.line(left_margin, 118, right_margin, 118)
	pdf.setFont("Helvetica", 10)
	pdf.setFillColor(colors.HexColor("#666666"))
	pdf.drawString(left_margin, 96, "Authorized Signature: ______________________________")
	pdf.drawString(left_margin, 76, "This is a system-generated invoice and does not require a physical stamp.")
	pdf.showPage()
	pdf.save()
	return response
