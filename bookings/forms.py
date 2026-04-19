from django import forms
from django.core.exceptions import ValidationError

from hostel.models import Bed, Room

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["room", "bed", "start_date", "end_date"]
        widgets = {
            "room": forms.Select(attrs={"class": "form-select", "id": "room"}),
            "bed": forms.Select(attrs={"class": "form-select", "id": "bed"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["room"].queryset = Room.objects.filter(available_beds__gt=0).select_related("hostel")
        self.fields["bed"].queryset = Bed.objects.none()

        room = None
        if self.data.get("room"):
            try:
                room = Room.objects.get(pk=self.data.get("room"))
            except (Room.DoesNotExist, ValueError, TypeError):
                room = None
        elif self.instance and self.instance.pk:
            room = self.instance.room

        if room:
            self.fields["bed"].queryset = Bed.objects.filter(is_available=True, room=room).select_related("room", "room__hostel")

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get("room")
        bed = cleaned_data.get("bed")

        if room and room.available_beds <= 0:
            raise ValidationError("Room is full")

        if room and bed and bed.room_id != room.id:
            raise ValidationError("Selected bed does not belong to selected room.")

        if bed and not bed.is_available:
            raise ValidationError("Selected bed is not available.")

        return cleaned_data
