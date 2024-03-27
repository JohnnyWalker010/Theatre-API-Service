from rest_framework import viewsets

from theatre_booking.models import (
    Actor,
    Genre,
    Reservation,
    TheatreHall,
    Play,
    Performance,
    Ticket,
)
from theatre_booking.serializers import (
    ActorSerializer,
    GenreSerializer,
    ReservationSerializer,
    TheatreHallSerializer,
    PlaySerializer,
    PerformanceSerializer,
    TicketSerializer, PlayListSerializer, PerformanceListSerializer, PerformanceDetailSerializer,
)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        return PlaySerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.prefetch_related("actors", "genres")
        return queryset


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        if self.action == "retrieve":
            return PerformanceDetailSerializer
        return PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == 'list':
            queryset = queryset.select_related("play")
        return queryset


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        return self.queryset.filter(reservation__user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        current_reservation = Reservation.objects.filter(user=user, status="active").first()
        if current_reservation:
            serializer.save(reservation=current_reservation)
        else:
            new_reservation = Reservation.objects.create(user=user, status="active")
            serializer.save(reservation=new_reservation)

    def perform_update(self, serializer):
        serializer.save()
