from django import forms

from .models import Complaint, ServiceRequest


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["issue", "image"]
        widgets = {
            "issue": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Describe your issue in detail..."}),
            "image": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ["request_type", "details"]
        widgets = {
            "request_type": forms.Select(attrs={"class": "form-select"}),
            "details": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Optional details"}),
        }
