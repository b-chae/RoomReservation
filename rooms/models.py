import sys
from io import BytesIO
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from core import models as core_models
from users import models as user_models
from cal import Calendar

# Create your models here.


class AbstractItem(core_models.TimeStampedModel):
    """Abstract Item """

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class RoomType(AbstractItem):

    class Meta:
        verbose_name = "Room Type"
        ordering = ['name']


class Amenity(AbstractItem):

    class Meta:
        verbose_name_plural = "Amenities"


class Facility(AbstractItem):

    class Meta:
        verbose_name_plural = "Facilities"


class HouseRule(AbstractItem):

    class Meta:
        verbose_name = "House Rule"


class Photo(core_models.TimeStampedModel):
    """Photo Model Definition """

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="room_photos/")
    room = models.ForeignKey(
        "Room", related_name="photos", on_delete=models.CASCADE)

    def __str__(self):
        return self.caption

    def save(self):
        image = Image.open(self.file)

        width = 100
        src_width, src_height = image.size
        src_ratio = float(src_height) / float(src_width)
        dst_height = round(src_ratio * width)

        output = BytesIO()

        im = image.resize((width, dst_height))

        im.save(output, format='PNG', quality=90)
        output.seek(0)

        self.file = InMemoryUploadedFile(output, 'ImageField', "%s.png" % self.file.name.split('.')[0], 'image/png',
                                         sys.getsizeof(output), None)

        super(Photo, self).save()


class Room(core_models.TimeStampedModel):

    """ Room Model Definition """

    name = models.CharField(max_length=140)
    description = models.TextField()
    country = CountryField()
    city = models.CharField(max_length=80)
    price = models.IntegerField()
    address = models.CharField(max_length=140)

    guests = models.IntegerField()
    beds = models.IntegerField()
    bedrooms = models.IntegerField()
    baths = models.IntegerField()

    check_in = models.TimeField()
    check_out = models.TimeField()
    instant_book = models.BooleanField(default=False)

    # one user can have multiple rooms, many-to-one relationship,
    # foreign key has user's identity key (id)
    host = models.ForeignKey(
        user_models.User, related_name="rooms", on_delete=models.CASCADE)
    room_type = models.ForeignKey(
        RoomType, related_name="rooms", on_delete=models.SET_NULL, null=True)
    amenities = models.ManyToManyField(
        Amenity, related_name="rooms", blank=True)
    facilities = models.ManyToManyField(
        Facility, related_name="rooms", blank=True)
    house_rules = models.ManyToManyField(
        HouseRule, related_name="rooms", blank=True)

    def save(self, *args, **kwargs):
        self.city = str.capitalize(self.city)
        super().save(*args, **kwargs)  # Call the real save() method

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    def total_rating(self):
        all_reviews = self.reviews.all()
        if len(all_reviews) == 0:
            return 0

        all_ratings = 0
        for review in all_reviews:
            all_ratings += review.rating_average()
        return round(all_ratings/len(all_reviews), 2)

    def total_accuracy(self):
        all_reviews = self.reviews.all()
        if len(all_reviews) == 0:
            return 0
        all_ratings = 0
        for review in all_reviews:
            all_ratings += review.accuracy
        return round(all_ratings/len(all_reviews), 2)

    def total_communication(self):
        all_reviews = self.reviews.all()
        if len(all_reviews) == 0:
            return 0

        all_ratings = 0
        for review in all_reviews:
            all_ratings += review.communication
        return round(all_ratings/len(all_reviews), 2)

    def total_cleanliness(self):
        all_reviews = self.reviews.all()
        if len(all_reviews) == 0:
            return 0

        all_ratings = 0
        for review in all_reviews:
            all_ratings += review.cleanliness
        return round(all_ratings/len(all_reviews), 2)

    def total_location(self):
        all_reviews = self.reviews.all()
        if len(all_reviews) == 0:
            return 0

        all_ratings = 0
        for review in all_reviews:
            all_ratings += review.location
        return round(all_ratings/len(all_reviews), 2)

    def total_check_in(self):
        all_reviews = self.reviews.all()
        if len(all_reviews) == 0:
            return 0

        all_ratings = 0
        for review in all_reviews:
            all_ratings += review.check_in
        return round(all_ratings/len(all_reviews), 2)

    def total_value(self):
        all_reviews = self.reviews.all()
        if(len(all_reviews) == 0):
            return 0

        all_ratings = 0
        for review in all_reviews:
            all_ratings += review.value
        return round(all_ratings/len(all_reviews), 2)

    def first_photo(self):
        try:
            photo, = self.photos.all()[:1]
            return photo.file.url
        except ValueError:
            return None

    def get_next_four_photos(self):
        try:
            photos = self.photos.all()[1:5]
            return photos
        except ValueError:
            return None

    def get_calendars(self):
        now = timezone.now()
        this_year = now.year
        this_month = now.month
        next_year = this_year
        next_month = this_month + 1
        if next_month == 13:
            next_year += 1
            next_month = 1
        this_month = Calendar(this_year, this_month)
        next_month = Calendar(next_year, next_month)
        return [this_month, next_month]
