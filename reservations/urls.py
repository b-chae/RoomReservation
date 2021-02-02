from django.urls import path
from . import views

app_name = "reservations"

urlpatterns = [
    path("confirm/<int:room>/<int:year>-<int:month>-<int:day>/",
         views.confirm, name="confirm"),
    path("create/<int:room>/<int:year>-<int:month>-<int:day>/",
         views.create, name="create"),
    path("<int:pk>/", views.ReservationDetail.as_view(), name="detail"),
    path("<int:pk>/<str:verb>", views.edit_reservation, name="edit"),
    path("lists/", views.reservations_list, name="lists"),
    path("<int:pk>/delete/", views.reservation_delete, name="delete"),
]
