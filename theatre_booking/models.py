from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Reservation of {self.user} at {self.created_at}"


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} with {self.capacity} capacity"


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    actors = models.ManyToManyField(Actor)
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return f"{self.title}"


class Performance(models.Model):
    play = models.ForeignKey(Play, on_delete=models.SET_NULL, null=True)
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.SET_NULL, null=True)
    showtime = models.DateTimeField()

    def __str__(self):
        return f"Performance at {self.showtime}"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    performance = models.ForeignKey(
        Performance, on_delete=models.SET_NULL, null=True, related_name="tickets"
    )
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("row", "seat", "performance")

    def clean(self):
        if self.performance:
            if not (
                1 <= self.row <= self.performance.theatre_hall.rows
                and 1 <= self.seat <= self.performance.theatre_hall.seats_in_row
            ):
                raise ValidationError(
                    {
                        "seat": f"Seat must be between 1 and {self.performance.theatre_hall.seats_in_row}",
                        "row": f"Row must be between 1 and {self.performance.theatre_hall.rows}",
                    }
                )
        else:
            raise ValidationError("Ticket must be associated with a performance")

    def __str__(self):
        performance_title = (
            self.performance.play.title if self.performance else "Unknown"
        )
        customer_name = (
            self.reservation.user.username
            if (self.reservation and self.reservation.user)
            else "Unknown"
        )
        reservation_time = (
            self.reservation.created_at if self.reservation else "Unknown"
        )
        return (
            f"Ticket {self.id}, "
            f"Performance: {performance_title}, "
            f"Customer: {customer_name}, "
            f"Seat: {self.seat}, Row: {self.row}, "
            f"Purchased at: {reservation_time}."
        )
