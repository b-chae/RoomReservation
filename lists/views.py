from django.contrib import messages
from django.views.generic import TemplateView
from django.shortcuts import redirect, reverse
from rooms import models as room_models
from . import models


def toggle_room(request, room_pk):
    room = room_models.Room.objects.get(pk=room_pk)
    if room is not None:
        the_list, _ = models.List.objects.get_or_create(
            user=request.user, name="My Favorite Houses")
        if room in the_list.rooms.all():
            the_list.rooms.remove(room)
            messages.success(request, "Removed from my favorite list")
        else:
            if the_list.rooms.count() < 20:
                the_list.rooms.add(room)
                messages.success(request, "Added to my favorite list")
            else:
                messages.error(request, "Too many rooms in your favorite list")
    else:
        messages.error(request, "Page Not Found")
        return redirect(reverse("core:home"))
    return redirect(reverse("rooms:detail", kwargs={"pk": room_pk}))


class SeeFavsView(TemplateView):
    template_name = "lists/list_detail.html"
