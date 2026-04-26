from django import forms

from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "message"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter announcement title"}
            ),
            "message": forms.Textarea(
                attrs={"class": "form-control", "rows": 5, "placeholder": "Write announcement details"}
            ),
        }
