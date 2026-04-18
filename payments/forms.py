from django import forms

from .models import Payment


class PaymentUpdateForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "status", "due_date", "paid_date"]
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "paid_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        }
