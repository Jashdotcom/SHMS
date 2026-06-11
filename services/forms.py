import os

from django import forms
from django.core.exceptions import ValidationError

from .models import Complaint, ServiceRequest


ALLOWED_ATTACHMENT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".doc", ".docx"}
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}


def validate_attachment_file(file_obj):
    if not file_obj:
        return
    extension = os.path.splitext(file_obj.name.lower())[1]
    if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValidationError("Unsupported file type. Upload an image, PDF, DOC, or DOCX file.")
    if file_obj.size > 10 * 1024 * 1024:
        raise ValidationError("File size must be 10 MB or less.")


def validate_image_file(file_obj):
    if not file_obj:
        return
    extension = os.path.splitext(file_obj.name.lower())[1]
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Unsupported image type. Upload a JPG, PNG, or GIF file.")
    if file_obj.size > 5 * 1024 * 1024:
        raise ValidationError("Image size must be 5 MB or less.")


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["issue", "image", "attachment"]
        widgets = {
            "issue": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Describe your issue in detail..."}),
            "image": forms.FileInput(attrs={"class": "form-control", "accept": "image/*", "data-preview-target": "#complaint-image-preview"}),
            "attachment": forms.FileInput(attrs={"class": "form-control", "accept": ".png,.jpg,.jpeg,.gif,.pdf,.doc,.docx", "data-preview-target": "#complaint-attachment-preview"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        validate_image_file(image)
        return image

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        validate_attachment_file(attachment)
        return attachment


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ["request_type", "details", "attachment"]
        widgets = {
            "request_type": forms.Select(attrs={"class": "form-select"}),
            "details": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Optional details"}),
            "attachment": forms.FileInput(attrs={"class": "form-control", "accept": ".png,.jpg,.jpeg,.gif,.pdf,.doc,.docx", "data-preview-target": "#service-attachment-preview"}),
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        validate_attachment_file(attachment)
        return attachment
