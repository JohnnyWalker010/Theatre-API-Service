from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIRequestFactory

from theatre_booking.models import (
    Actor,
    Genre,
    Reservation,
    TheatreHall,
    Play,
    Performance,
    Ticket,
)
from .serializers import (
    GenreSerializer,
    ActorSerializer,
    ReservationSerializer,
    PerformanceSerializer,
    TheatreHallSerializer,
)
from .views import (
    ActorViewSet,
    GenreViewSet,
    TheatreHallViewSet,
    PlayViewSet,
    TicketViewSet,
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


class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword1"
        )
        self.actor = Actor.objects.create(first_name="John", last_name="Doe")
        self.genre = Genre.objects.create(name="Drama")
        self.hall = TheatreHall.objects.create(
            name="Test Hall", rows=15, seats_in_row=15
        )
        self.play = Play.objects.create(
            title="Test play", description="Test description"
        )
        self.play.actors.add(self.actor)
        self.play.genres.add(self.genre)
        self.performance = Performance.objects.create(
            play=self.play, theatre_hall=self.hall, showtime=timezone.now()
        )
        self.reservation = Reservation.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            row=5, seat=10, performance=self.performance, reservation=self.reservation
        )

    def test_actor_str(self):
        actor = Actor.objects.get(first_name="John")
        self.assertEqual(str(actor), "John Doe")

    def test_genre_str(self):
        genre = Genre.objects.get(name="Drama")
        self.assertEqual(str(genre), "Drama")

    def test_reservation_str(self):
        reservation = Reservation.objects.get(user=self.user)
        self.assertEqual(
            str(reservation), f"Reservation of {self.user} at {reservation.created_at}"
        )

    def test_theatre_hall_str(self):
        hall = TheatreHall.objects.get(name="Test Hall")
        self.assertEqual(str(hall), "Test Hall with 225 capacity")

    def test_play_str(self):
        play = Play.objects.get(title="Test play")
        self.assertEqual(str(play), "Test play")

    def test_performance_str(self):
        performance = Performance.objects.get(play=self.play)
        self.assertEqual(str(performance), f"Performance at {performance.showtime}")

    def test_ticket_str(self):
        ticket = Ticket.objects.get(id=self.ticket.id)
        expected_str = (
            f"Ticket {ticket.id}, Performance: Test play, Customer: testuser, Seat: 10, Row: 5, Purchased "
            f"at: {ticket.reservation.created_at}."
        )
        self.assertEqual(str(ticket), expected_str)

    def test_ticket_clean(self):
        invalid_ticket = Ticket(
            row=20, seat=30, performance=self.performance, reservation=self.reservation
        )
        self.assertRaises(ValidationError, invalid_ticket.clean)

    def test_ticket_clean_no_performance(self):
        ticket_without_performance = Ticket(
            row=5, seat=10, reservation=self.reservation
        )
        self.assertRaises(ValidationError, ticket_without_performance.clean)


class ViewsTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.actor1 = Actor.objects.create(first_name="John", last_name="Doe")
        self.genre1 = Genre.objects.create(name="Drama")
        self.theatre_hall1 = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=15
        )
        self.play1 = Play.objects.create(
            title="Romeo and Juliet", description="A tragic love story"
        )
        self.performance1 = Performance.objects.create(
            play=self.play1,
            theatre_hall=self.theatre_hall1,
            showtime="2024-03-28 14:00:00",
        )
        self.reservation1 = Reservation.objects.create(user=self.user)
        self.ticket1 = Ticket.objects.create(
            row=5, seat=10, performance=self.performance1, reservation=self.reservation1
        )

    def test_actor_list(self):
        view = ActorViewSet.as_view({"get": "list"})
        request = self.factory.get(reverse("theatre_service:actor-list"))
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_genre_list(self):
        view = GenreViewSet.as_view({"get": "list"})
        request = self.factory.get(reverse("theatre_service:genre-list"))
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_theatre_hall_retrieve(self):
        view = TheatreHallViewSet.as_view({"get": "retrieve"})
        request = self.factory.get(
            reverse("theatre_service:theatrehall-detail", args=[self.theatre_hall1.id])
        )
        response = view(request, pk=self.theatre_hall1.id)
        self.assertEqual(response.status_code, 200)

    def test_play_list(self):
        view = PlayViewSet.as_view({"get": "list"})
        request = self.factory.get(reverse("theatre_service:play-list"))
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_ticket_list(self):
        view = TicketViewSet.as_view({"get": "list"})
        request = self.factory.get(reverse("theatre_service:ticket-list"))
        request.user = self.user
        response = view(request)
        self.assertEqual(response.status_code, 200)


class TestActorSerializer(TestCase):
    def test_actor_serializer_valid(self):
        data = {"first_name": "John", "last_name": "Doe"}
        serializer = ActorSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class TestGenreSerializer(TestCase):
    def test_genre_serializer_valid(self):
        data = {"name": "Drama"}
        serializer = GenreSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class TestReservationSerializer(TestCase):
    def test_reservation_serializer_valid(self):
        user = User.objects.create(username="testuser")
        data = {"user": user.id}
        serializer = ReservationSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class TestTheatreHallSerializer(TestCase):
    def test_theatre_hall_serializer_valid(self):
        data = {"name": "Main Hall", "rows": 10, "seats_in_row": 15}
        serializer = TheatreHallSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class TestPerformanceSerializer(TestCase):
    def test_performance_serializer_valid(self):
        play = Play.objects.create(title="Hamlet", description="Tragedy")
        theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=15
        )
        data = {
            "play": play.id,
            "theatre_hall": theatre_hall.id,
            "showtime": "2024-03-28 14:00:00",
        }
        serializer = PerformanceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
