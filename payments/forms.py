from django import forms

from .models import Payment


class PaymentUpdateForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "status"]
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
