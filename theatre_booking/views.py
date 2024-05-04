from drf_spectacular.utils import extend_schema, OpenApiParameter
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
    TicketSerializer,
    PlayListSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer

    @extend_schema(
        description="List all actors",
        parameters=[
            OpenApiParameter(
                name="str_parameter",
                type=str,
                description="First additional parameter...",
                required=False,
            ),
            OpenApiParameter(
                name="list_parameter",
                type={"type": "list", "items": {"type": "number"}},
                description="Second additional parameter...",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(description="Retrieve a specific actor")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(description="Create a new actor")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(description="Update an existing actor")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(description="Partially update an existing actor")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(description="Delete an existing actor")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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
        return self.serializer_class

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
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.select_related("play")
        return queryset


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        return self.queryset.filter(reservation__user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        current_reservation = Reservation.objects.filter(
            user=user, status="active"
        ).first()
        if current_reservation:
            serializer.save(reservation=current_reservation)
        else:
            new_reservation = Reservation.objects.create(user=user, status="active")
            serializer.save(reservation=new_reservation)

    def perform_update(self, serializer):
        serializer.save()
