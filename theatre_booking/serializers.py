from rest_framework import serializers

from theatre_booking.models import (
    Actor,
    Genre,
    Reservation,
    TheatreHall,
    Performance,
    Ticket,
    Play,
)


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")
        read_only_fields = ("id",)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")
        read_only_fields = ("id",)


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("id", "created_at", "user")
        read_only_fields = ("id", "created_at")


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row")
        read_only_fields = ("id",)


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "actors", "genres")
        read_only_fields = ("id",)


class PlayListSerializer(PlaySerializer):
    actors = ActorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "showtime")
        read_only_fields = ("id",)


class PerformanceListSerializer(PerformanceSerializer):
    play = PlaySerializer(many=False, read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")
        read_only_fields = ("id", "reservation")


class PerformanceDetailSerializer(PerformanceSerializer):
    theatre_hall = TheatreHallSerializer(many=False, read_only=True)
    available_seats = serializers.SerializerMethodField()

    @staticmethod
    def get_available_seats(obj):
        sold_tickets_count = Ticket.objects.filter(performance=obj).count()
        total_seats = obj.theatre_hall.capacity
        available_seats = total_seats - sold_tickets_count

        return available_seats if available_seats else "Sold out!"

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "showtime", "available_seats")
