from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django_countries import countries
from .import models

# Limiting Querysets
# all_rooms = models.Room.objects.all()[:5]
# just pointing the DB, not loading

# url에서 오는 모든 것은 Get Request 이다 !
# print(request.GET)
# http://127.0.0.1:8000/?page=1&city=seoul


class HomeView(ListView):
    """ HomeView Definition """

    model = models.Room
    paginate_by = 10
    paginate_orphans = 5
    ordering = "created"
    page_kwarg = "page"


class RoomDetail(DetailView):

    """ Room Detail Definition """

    model = models.Room
    pk_url_kwarg = "pk"


def search(request):
    city = request.GET.get("city", "Anywhere")
    city = str.capitalize(city)
    country = request.GET.get("country", "KR")
    room_type = int(request.GET.get("room_type", 0))
    price = int(request.GET.get("price", 0))
    guests = int(request.GET.get("guests", 0))
    bedrooms = int(request.GET.get("bedrooms", 0))
    beds = int(request.GET.get("beds", 0))
    baths = int(request.GET.get("baths", 0))
    instant = bool(request.GET.get("instant", False))
    superhost = bool(request.GET.get("superhost", False))
    s_amenities = request.GET.getlist("amenities")
    s_facilities = request.GET.getlist("facilities")
    s_house_rules = request.GET.getlist("house_rules")

    room_types = models.RoomType.objects.all()
    amenities = models.Amenity.objects.all()
    facilities = models.Facility.objects.all()
    house_rules = models.HouseRule.objects.all()

    form = {"city": city,
            "s_country": country,
            "s_room_type": room_type,
            "price": price,
            "guests": guests,
            "bedrooms": bedrooms,
            "beds": beds,
            "baths": baths,
            "instant": instant,
            "superhost": superhost,
            "s_amenities": s_amenities,
            "s_facilities": s_facilities,
            "s_house_rules": s_house_rules,
            }
    choices = {"countries": countries,
               "room_types": room_types,
               "amenities": amenities,
               "facilities": facilities,
               "house_rules": house_rules, }

    filter_args = {}
    if city != "Anywhere":
        filter_args["city__startswith"] = city
    filter_args["country"] = country

    if room_type != 0:
        filter_args["room_type__pk__exact"] = room_type

    if price != 0:
        filter_args["price__lte"] = price

    if guests != 0:
        filter_args["guests__gte"] = guests

    if bedrooms != 0:
        filter_args["bedrooms__gte"] = bedrooms

    if beds != 0:
        filter_args["beds__gte"] = beds

    if guests != 0:
        filter_args["guests__gte"] = guests

    if baths != 0:
        filter_args["baths__gte"] = baths

    if instant is True:
        filter_args["instant_book"] = True

    if superhost is True:
        filter_args["host__superhost"] = True

    for s_amenity in s_amenities:
        filter_args["amenities__pk"] = int(s_amenity)

    for s_facility in s_facilities:
        filter_args["facilities__pk"] = int(s_facility)

    for s_house_rule in s_house_rules:
        filter_args["house_urles__pk"] = int(s_house_rule)

    rooms = models.Room.objects.filter(**filter_args)

    return render(request, "rooms/search.html",
                  {**form, **choices, "rooms": rooms})
