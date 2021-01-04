from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from .import models


def all_rooms(request):
    # Limiting Querysets
    # all_rooms = models.Room.objects.all()[:5]
    # just pointing the DB, not loading

    # url에서 오는 모든 것은 Get Request 이다 !
    # print(request.GET)
    # http://127.0.0.1:8000/?page=1&city=seoul

    page = int(request.GET.get("page", 1) or 1)
    room_list = models.Room.objects.all()
    paginator = Paginator(room_list, 10, orphans=3)
    rooms = paginator.get_page(page)
    print(vars(rooms.paginator))

    return render(request, "rooms/home.html",
                  context={
                      "pages": rooms,
                  })
