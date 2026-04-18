from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User

from .forms import PaymentUpdateForm
from .models import Payment


def _is_admin_user(user):
	return user.is_authenticated and (user.is_staff or user.role == User.ROLE_ADMIN)


@login_required
def payment_list_view(request):
	payments = Payment.objects.select_related("user")
	if request.user.role != User.ROLE_ADMIN and not request.user.is_staff:
		payments = payments.filter(user=request.user)
	return render(request, "payments/payments.html", {"payments": payments})


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
