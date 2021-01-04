from math import ceil
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from .import models


def all_rooms(request):
    # Limiting Querysets
    # models.Room.objects.all()[5:10] 이게 모든 걸 가져와서 -> 제한
    # 하는 게 아니라 5~10까지만 가져오는 것을 뜻함
    # all_rooms = models.Room.objects.all()[:5]

    # url에서 오는 모든 것은 Get Request 이다 !
    # print(request.GET)
    # http://127.0.0.1:8000/?page=1&city=seoul

    page = int(request.GET.get("page", 1) or 1)
    page_size = 10
    limit = page_size * page
    offset = limit - page_size
    all_rooms = models.Room.objects.all()[offset:limit]
    page_count = ceil(models.Room.objects.count() / page_size)

    return render(request, "rooms/home.html",
                  context={
                      "rooms": all_rooms,
                      "page": page,
                      "page_count": page_count,
                      "page_range": range(1, page_count+1),
                  })
