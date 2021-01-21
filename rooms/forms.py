from django import forms
from django_countries.fields import CountryField
from . import models


class SearchForm(forms.Form):

    city = forms.CharField(initial="Anywhere")
    country = CountryField(default="KR").formfield()
    price = forms.IntegerField(required=False, min_value=0)
    room_type = forms.ModelChoiceField(
        empty_label="Any kind",
        queryset=models.RoomType.objects.all(),
        required=False
    )
    price = forms.IntegerField(required=False, min_value=0)
    guests = forms.IntegerField(required=False, min_value=0, max_value=10)
    bedrooms = forms.IntegerField(required=False, min_value=0, max_value=10)
    beds = forms.IntegerField(required=False, min_value=0, max_value=10)
    baths = forms.IntegerField(required=False, min_value=0, max_value=10)
    instant_book = forms.BooleanField(required=False)
    superhost = forms.BooleanField(required=False)
    amenities = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    facilities = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Facility.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )


class CreatePhotoForm(forms.ModelForm):
    class Meta:
        model = models.Photo
        fields = ("caption", "file")

    def save(self, pk, *args, **kwargs):
        photo = super().save(commit=False)
        room = models.Room.objects.get(pk=pk)
        photo.room = room
        photo.save()
