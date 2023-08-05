from hadrian.contrib.locations.models import Location
from django import forms

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location