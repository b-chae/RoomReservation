from django.contrib import admin
from . import models


@admin.register(models.RoomType, models.Facility,
                models.Amenity, models.HouseRule)
class ItemAdmin(admin.ModelAdmin):

    """ Item Admin Definition """

    pass


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):

    """ Room Admin Definition """

    fieldsets = (
        (
            "Basic Info",
            {"fields": ("name", "description", "country", "address", "price")},
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
                    "beds", "baths", "check_in", "check_out", "instant_book", "count_amenities")
    list_filter = ("instant_book", "host__superhost", "room_type",
                   "amenities", "facilities", "house_rules", "country", "city")
    search_fields = ("=city", "=host__username", "name")
    filter_horizontal = ("amenities", "facilities", "house_rules")
    ordering = ("price", "name")

    # object : current row
    def count_amenities(self, obj):
        return obj.amenities.count()


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass
