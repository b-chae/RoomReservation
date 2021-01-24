import datetime
from django.http import Http404
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from rooms import models as room_models
from . import models


class CreateError(Exception):
    pass


def create(request, room, year, month, day):
    try:
        date_obj = datetime.datetime(year=year, month=month, day=day)
        room = room_models.Room.objects.get(pk=room)
        models.BookedDay.objects.get(day=date_obj, reservation__room=room)
        raise CreateError()
    except (room_models.Room.DoesNotExist, CreateError):
        messages.error(request, "Can't reserve that room")
        return redirect(reverse("core:home"))
    except models.BookedDay.DoesNotExist:
        reservation = models.Reservation.objects.create(
            guest=request.user,
            room=room,
            check_in=date_obj,
            check_out=date_obj + datetime.timedelta(days=1),

        )
        return redirect(reverse("reservations:detail",
                                kwargs={"pk": reservation.pk}))


class ReservationDetail(View):
    def get(self, *args, **kwargs):
        reservation = models.Reservation.objects.get_or_none(pk=kwargs['pk'])
        if not reservation:
            raise Http404()
        elif reservation.guest != self.request.user and reservation.room.host != self.request.user:
            raise Http404()
        return render(self.request, "reservations/detail.html", {"reservation": reservation})
