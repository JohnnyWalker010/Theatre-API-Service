from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from theatre_booking.models import (
    Actor,
    Genre,
    Reservation,
    TheatreHall,
    Play,
    Performance,
    Ticket,
)


class AdminPanelTestCase(TestCase):
    def setUp(self):
        self.admin_username = "superadmin"
        self.admin_password = "SuperAdminPassword1"

        self.admin_user = User.objects.create_superuser(
            username=self.admin_username,
            email="admin@example.com",
            password=self.admin_password,
        )
        self.client = Client()

        self.actor = Actor.objects.create(first_name="John", last_name="Doe")
        self.genre = Genre.objects.create(name="Drama")
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=15
        )
        self.play = Play.objects.create(
            title="Hamlet",
            description="A tragedy by William Shakespeare",
        )
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            showtime="2024-04-01 18:00:00",
        )
        self.reservation = Reservation.objects.create(
            user=self.admin_user,
        )
        self.ticket = Ticket.objects.create(
            row=5,
            seat=10,
            performance=self.performance,
            reservation=self.reservation,
        )

    def test_admin_login(self):
        response = self.client.get(reverse("admin:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Log in" in str(response.content))
        login_data = {
            "username": self.admin_username,
            "password": self.admin_password,
        }
        response = self.client.post(reverse("admin:login"), login_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session["_auth_user_id"])

    def test_create_objects_via_admin(self):
        self.client.login(username=self.admin_username, password=self.admin_password)
        response = self.client.post(
            reverse("admin:theatre_booking_actor_add"),
            {"first_name": "Jane", "last_name": "Doe"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Actor.objects.filter(first_name="Jane", last_name="Doe").exists()
        )

    def test_update_objects_via_admin(self):
        self.client.login(username=self.admin_username, password=self.admin_password)
        actor_id = self.actor.id
        response = self.client.post(
            reverse("admin:theatre_booking_actor_change", args=(actor_id,)),
            {"first_name": "Updated First Name", "last_name": "Updated Last Name"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Actor.objects.filter(
                id=actor_id,
                first_name="Updated First Name",
                last_name="Updated Last Name",
            ).exists()
        )

    def test_delete_objects_via_admin(self):
        self.client.login(username=self.admin_username, password=self.admin_password)

        actor_id = self.actor.id
        response = self.client.post(
            reverse("admin:theatre_booking_actor_delete", args=(actor_id,)),
            {"post": "yes"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Actor.objects.filter(id=actor_id).exists())
