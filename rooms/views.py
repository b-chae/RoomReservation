from django.views.generic import ListView, DetailView
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
