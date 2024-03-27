from django.contrib.auth.models import User
from django.db import models


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=255)


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def get_hall_capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"Hall {self.name} with {self.get_hall_capacity()} capacity"


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    actors = models.ManyToManyField(Actor)
    genres = models.ManyToManyField(Genre)


class Performance(models.Model):
    play = models.ForeignKey(Play, on_delete=models.SET_NULL, null=True)
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.SET_NULL, null=True)
    showtime = models.DateTimeField()


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(Performance, on_delete=models.SET_NULL, null=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"Ticket {self.id},"
            f"Performance {self.performance.play.title},"
            f"Customer:{self.reservation.user}"
            f" Seat: {self.seat}, Row: {self.row}"
            f"Purchased at: {self.reservation.created_at}"
        )
