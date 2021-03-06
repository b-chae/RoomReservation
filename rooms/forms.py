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
    price = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(
        attrs={'placeholder': 'Maximum Price'}))
    guests = forms.IntegerField(required=False, min_value=0,
                                max_value=10, widget=forms.NumberInput(attrs={'class': 'h-10'}))
    bedrooms = forms.IntegerField(
        required=False, min_value=0, max_value=10, widget=forms.NumberInput(attrs={'class': 'h-10'}))
    beds = forms.IntegerField(required=False, min_value=0, max_value=10,
                              widget=forms.NumberInput(attrs={'class': 'h-10'}))
    baths = forms.IntegerField(required=False, min_value=0, max_value=10,
                               widget=forms.NumberInput(attrs={'class': 'h-10'}))
    instant_book = forms.BooleanField(
        required=False)
    superhost = forms.BooleanField(required=False)
    amenities = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Amenity.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'h-48'}),
    )
    facilities = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Facility.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'h-48'}),
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


class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = models.Room
        fields = (
            "name",
            "description",
            "country",
            "city",
            "price",
            "address",
            "guests",
            "beds",
            "bedrooms",
            "baths",
            "check_in",
            "check_out",
            "instant_book",
            "room_type",
            "amenities",
            "facilities",
            "house_rules",
        )

    def save(self, user, *args, **kwargs):
        room = super().save(commit=False)
        return room
