from django.contrib import admin
from django.utils.html import mark_safe
from . import models


@admin.register(models.RoomType, models.Facility,
                models.Amenity, models.HouseRule)
class ItemAdmin(admin.ModelAdmin):

    """ Item Admin Definition """

    list_display = ("name", "used_by",)

    def used_by(self, obj):
        return obj.rooms.count()


class PhotoInline(admin.StackedInline):

    model = models.Photo


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):

    """ Room Admin Definition """

    inlines = (PhotoInline, )

    fieldsets = (
        (
            "Basic Info",
            {"fields": ("name", "description", "country",
                        "city", "address", "price")},
        ),
        (
            "Times",
            {"fields": ("check_in", "check_out", "instant_book")},
        ),
        (
            "Spaces",
            {"fields": ("guests", "beds", "bedrooms", "baths",)},
        ),
        (
            "More About the Space",
            {
                "classes": ("collapse",),
                "fields": ("amenities", "facilities", "house_rules")},
        ),
        (
            "Host",
            {"fields": ("host",)},
        ),
    )

    list_display = ("name", "country", "city", "price", "guests",
                    "beds", "baths", "check_in", "check_out", "instant_book", "count_amenities", "count_photos", "total_rating")
    list_filter = ("instant_book", "host__superhost", "room_type",
                   "amenities", "facilities", "house_rules", "country", "city")
    search_fields = ("=city", "=host__username", "name")
    filter_horizontal = ("amenities", "facilities", "house_rules")
    ordering = ("price", "name")
    raw_id_fields = ("host", )

    # object : current row
    def count_amenities(self, obj):
        return obj.amenities.count()

    def count_photos(self, obj):
        return obj.photos.count()


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):

    """ Photo Admin Definition """

    list_display = ('__str__', 'get_thumbnail')

    def get_thumbnail(self, obj):
        return mark_safe(f'<img height="50px" src="{obj.file.url}" />')

    get_thumbnail.short_description = "Thumbnail"
