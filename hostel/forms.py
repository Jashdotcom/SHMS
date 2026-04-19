from django import forms

from .models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["hostel", "room_number", "room_type", "available_beds"]
        widgets = {
            "hostel": forms.Select(attrs={"class": "form-select"}),
            "room_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. A-101"}),
            "room_type": forms.Select(attrs={"class": "form-select"}),
            "available_beds": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }

    def clean(self):
        cleaned_data = super().clean()
        room_type = cleaned_data.get("room_type")
        available_beds = cleaned_data.get("available_beds")

        capacity_by_type = {
            Room.TYPE_SINGLE: 1,
            Room.TYPE_DOUBLE: 2,
            Room.TYPE_TRIPLE: 3,
            Room.TYPE_DORM: 4,
        }
        capacity = capacity_by_type.get(room_type)

        if capacity is not None and available_beds is not None and available_beds > capacity:
            raise forms.ValidationError("Available beds cannot exceed capacity")

        return cleaned_data
