import datetime
from django.http import Http404
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.db.models import Q
from rooms import models as room_models
from reviews import forms as review_forms
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
        elif (reservation.guest != self.request.user
              and reservation.room.host != self.request.user):
            raise Http404()
        form = review_forms.CreateReviewForm()
        return render(
            self.request,
            "reservations/detail.html",
            {"reservation": reservation,
             "form": form,
             })


def edit_reservation(request, pk, verb):

    reservation = models.Reservation.objects.get_or_none(pk=pk)
    if not reservation:
        raise Http404()
    if not reservation or (
        reservation.guest != request.user
        and reservation.room.host != request.user
    ):
        raise Http404()

    if verb == "confirm":
        if reservation.room.host != request.user:
            raise Http404()
        reservation.status = models.Reservation.STATUS_CONFIRMED
    elif verb == "cancel":
        reservation.status = models.Reservation.STATUS_CANCELED
        models.BookedDay.objects.filter(reservation=reservation).delete()
    reservation.save()
    messages.success(request, "Reservation updates!")
    return render(
        request,
        "reservations/detail.html",
        {"reservation": reservation})


def reservations_list(request):
    reservations = models.Reservation.objects.filter(
        Q(guest=request.user) | Q(room__host=request.user))

    return render(request, "reservations/lists.html", {"reservations": reservations})
