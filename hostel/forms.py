from django import forms

from .models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["hostel", "room_number", "room_type"]
        widgets = {
            "hostel": forms.Select(attrs={"class": "form-select"}),
            "room_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. A-101"}),
            "room_type": forms.Select(attrs={"class": "form-select"}),
        }
