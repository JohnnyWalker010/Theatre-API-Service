from django.contrib import admin

from theatre_booking.models import (
    Actor,
    Genre,
    Reservation,
    TheatreHall,
    Play,
    Performance,
    Ticket
)

admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(Reservation)
admin.site.register(TheatreHall)
admin.site.register(Play)
admin.site.register(Performance)
admin.site.register(Ticket)
