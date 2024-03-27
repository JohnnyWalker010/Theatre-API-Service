from django.urls import include, path
from rest_framework import routers

from theatre_booking.views import (
    ActorViewSet,
    GenreViewSet,
    ReservationViewSet,
    TheatreHallViewSet,
    PlayViewSet,
    PerformanceViewSet,
    TicketViewSet,
)

router = routers.DefaultRouter()
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("theatre-halls", TheatreHallViewSet)
router.register("plays", PlayViewSet)
router.register("performances", PerformanceViewSet)
router.register("reservations", ReservationViewSet)
router.register("ticket", TicketViewSet)


urlpatterns = [path("/", include(router.urls))]

app_name = "theatre_service"
