from django.views.generic import ListView, DetailView, View, UpdateView
from django.shortcuts import render
from django.core.paginator import Paginator
from .import models, forms

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


class SearchView(View):

    def get(self, request):
        country = request.GET.get("country")
        if country:
            form = forms.SearchForm(request.GET)
            if form.is_valid():
                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                price = form.cleaned_data.get("price")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                bedrooms = form.cleaned_data.get("bedrooms")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")

                filter_args = {}
                if city != "Anywhere":
                    filter_args["city__startswith"] = city
                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price__lte"] = price

                if guests is not None:
                    filter_args["guests__gte"] = guests

                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms

                if beds is not None:
                    filter_args["beds__gte"] = beds

                if guests is not None:
                    filter_args["guests__gte"] = guests

                if baths is not None:
                    filter_args["baths__gte"] = baths

                if instant_book is True:
                    filter_args["instant_book"] = True

                if superhost is True:
                    filter_args["host__superhost"] = True

                for amenity in amenities:
                    filter_args["amenities"] = amenity

                for facility in facilities:
                    filter_args["facilities"] = facility

                qs = models.Room.objects.filter(
                    **filter_args).order_by("created")
                paginator = Paginator(qs, 10, orphans=5)
                page = int(request.GET.get("page", 1))
                rooms = paginator.get_page(page)

                getstr = ""
                for i in form.data:
                    if i != "page":
                        getstr += '&' + i + '=' + form.data.get(i)
                return render(request, "rooms/search.html", {"form": form, "rooms": rooms, "page_obj": paginator.page(page), "getstr": getstr, })
        else:
            form = forms.SearchForm()

        return render(request, "rooms/search.html", {"form": form})


class EditRoomView(UpdateView):

    model = models.Room
    template_name = "rooms/room_edit.html"
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
