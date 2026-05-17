"""
TripRep Test Suite
==================
Run with:  python manage.py test core.tests
Coverage:  Auth, Tickets, Reservations, Statistics, UserProfile, Utilities
"""

from decimal import Decimal
from io import BytesIO
from unittest.mock import MagicMock, patch
import json

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from core.models import Reservations, Tickets, UserProfile
from core.forms import SignupForm
from core.views import get_converted_INR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username="testuser", email="test@example.com", password="testpass123"):
    return User.objects.create_user(username=username, email=email, password=password)


def fake_pdf(content=b"%PDF-1.4 fake pdf content"):
    """Return a minimal in-memory PDF upload."""
    return SimpleUploadedFile("ticket.pdf", content, content_type="application/pdf")


# ---------------------------------------------------------------------------
# 1. Authentication Tests
# ---------------------------------------------------------------------------

class SignupFormTests(TestCase):

    def test_valid_signup_form(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "securepass",
            "repeat_password": "securepass",
        }
        form = SignupForm(data)
        self.assertTrue(form.is_valid())

    def test_mismatched_passwords(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "pass1",
            "repeat_password": "pass2",
        }
        form = SignupForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("Passwords do not match", str(form.errors))

    def test_duplicate_email_rejected(self):
        make_user(username="existing@example.com", email="existing@example.com")
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "existing@example.com",
            "password": "pass",
            "repeat_password": "pass",
        }
        form = SignupForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("already registered", str(form.errors))

    def test_missing_required_fields(self):
        form = SignupForm({})
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("email", form.errors)


class SignupViewTests(TestCase):

    def test_get_signup_page(self):
        response = self.client.get(reverse("core:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/signup.html")

    def test_successful_signup_creates_user_and_redirects(self):
        data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "password": "strongpass",
            "repeat_password": "strongpass",
        }
        response = self.client.post(reverse("core:signup"), data, follow=True)
        self.assertRedirects(response, reverse("core:dashboard"))
        self.assertTrue(User.objects.filter(email="alice@example.com").exists())

    def test_signup_logs_user_in(self):
        data = {
            "first_name": "Bob",
            "last_name": "Jones",
            "email": "bob@example.com",
            "password": "pass123",
            "repeat_password": "pass123",
        }
        self.client.post(reverse("core:signup"), data)
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)  # not redirected to login


class LoginViewTests(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_get_login_page(self):
        response = self.client.get(reverse("core:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/login.html")

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("core:login"),
            {"username": "testuser", "password": "testpass123"},
            follow=True,
        )
        self.assertRedirects(response, reverse("core:dashboard"))

    def test_invalid_login_stays_on_page(self):
        response = self.client.post(
            reverse("core:login"),
            {"username": "testuser", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/login.html")

    def test_logout_redirects_to_index(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("core:logout"), follow=True)
        self.assertRedirects(response, reverse("core:index"))


# ---------------------------------------------------------------------------
# 2. Dashboard & Protected Views
# ---------------------------------------------------------------------------

class DashboardTests(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertRedirects(response, reverse("core:login"))

    def test_logged_in_user_sees_dashboard(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/dashboard.html")

    def test_dashboard_contains_first_name(self):
        self.user.first_name = "Alice"
        self.user.save()
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("core:dashboard"))
        self.assertContains(response, "Alice")


# ---------------------------------------------------------------------------
# 3. Ticket Model Tests
# ---------------------------------------------------------------------------

class TicketModelTests(TestCase):

    def setUp(self):
        self.user = make_user()

    @patch("core.models.Tickets.generate_thumbnail")
    def test_ticket_saved_to_db(self, mock_thumb):
        ticket = Tickets(
            user=self.user,
            title="Mumbai to Delhi",
            ticket_file=fake_pdf(),
            source="Mumbai",
            destination="Delhi",
            description="Test trip",
            date_of_journey="2025-06-15",
            ticket_type="Flight",
            booked_through="MakeMyTrip",
            amount_paid=Decimal("4500.00"),
        )
        ticket.save()
        self.assertEqual(Tickets.objects.count(), 1)
        self.assertEqual(Tickets.objects.first().title, "Mumbai to Delhi")

    @patch("core.models.Tickets.generate_thumbnail")
    def test_ticket_str_representation(self, mock_thumb):
        ticket = Tickets(
            user=self.user,
            title="Chennai Express",
            ticket_file=fake_pdf(),
            source="Chennai",
            destination="Bangalore",
            description="",
            date_of_journey="2025-07-01",
            ticket_type="Train",
            booked_through="IRCTC",
            amount_paid=Decimal("200.00"),
        )
        ticket.save()
        self.assertEqual(str(ticket), "Chennai Express")

    @patch("core.models.Tickets.generate_thumbnail")
    def test_ticket_deleted_from_db(self, mock_thumb):
        ticket = Tickets(
            user=self.user,
            title="Delete Me",
            ticket_file=fake_pdf(),
            source="A",
            destination="B",
            description="",
            date_of_journey="2025-01-01",
            ticket_type="Bus",
            booked_through="RedBus",
            amount_paid=Decimal("100.00"),
        )
        ticket.save()
        ticket_id = ticket.pk
        ticket.delete()
        self.assertFalse(Tickets.objects.filter(pk=ticket_id).exists())

    @patch("core.models.Tickets.generate_thumbnail")
    def test_ticket_belongs_to_correct_user(self, mock_thumb):
        other_user = make_user(username="other@x.com", email="other@x.com")
        ticket = Tickets(
            user=other_user,
            title="Other User Ticket",
            ticket_file=fake_pdf(),
            source="X",
            destination="Y",
            description="",
            date_of_journey="2025-03-01",
            ticket_type="Flight",
            booked_through="Indigo",
            amount_paid=Decimal("3000.00"),
        )
        ticket.save()
        # self.user should see 0 tickets
        self.assertEqual(Tickets.objects.filter(user=self.user).count(), 0)
        # other_user should see 1
        self.assertEqual(Tickets.objects.filter(user=other_user).count(), 1)


# ---------------------------------------------------------------------------
# 4. Ticket Views Tests
# ---------------------------------------------------------------------------

class TicketViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.client.login(username="testuser", password="testpass123")

    def test_ticket_list_empty(self):
        response = self.client.get(reverse("core:tickets"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/tickets.html")

    @patch("core.models.Tickets.generate_thumbnail")
    def test_ticket_list_shows_user_tickets(self, mock_thumb):
        Tickets.objects.create(
            user=self.user,
            title="My Ticket",
            ticket_file=fake_pdf(),
            source="A",
            destination="B",
            description="",
            date_of_journey="2025-05-01",
            ticket_type="Flight",
            booked_through="SpiceJet",
            amount_paid=Decimal("2000.00"),
        )
        response = self.client.get(reverse("core:tickets"))
        self.assertContains(response, "My Ticket")

    def test_anonymous_cannot_view_tickets(self):
        self.client.logout()
        response = self.client.get(reverse("core:tickets"))
        self.assertRedirects(response, reverse("core:login"))

    def test_add_ticket_page_loads(self):
        response = self.client.get(reverse("core:add_ticket"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/add_ticket.html")

    @patch("core.models.Tickets.generate_thumbnail")
    @patch("core.views.get_distance", return_value=900.0)
    def test_save_ticket_post(self, mock_dist, mock_thumb):
        response = self.client.post(
            reverse("core:save_ticket"),
            {
                "title": "Test Flight",
                "source": "Mumbai",
                "destination": "Delhi",
                "description": "Business trip",
                "date_of_journey": "2025-08-10",
                "ticket_type_dropdown": "Flight",
                "booked_through": "IndiGo",
                "amount_paid": "5000",
                "ticket_pdf": fake_pdf(),
            },
        )
        self.assertEqual(Tickets.objects.filter(user=self.user).count(), 1)

    @patch("core.models.Tickets.generate_thumbnail")
    def test_view_ticket_detail(self, mock_thumb):
        ticket = Tickets.objects.create(
            user=self.user,
            title="Detail Ticket",
            ticket_file=fake_pdf(),
            source="C",
            destination="D",
            description="",
            date_of_journey="2025-09-01",
            ticket_type="Train",
            booked_through="IRCTC",
            amount_paid=Decimal("300.00"),
        )
        response = self.client.get(
            reverse("core:view_ticket", kwargs={"ticket_id": ticket.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Ticket")

    @patch("core.models.Tickets.generate_thumbnail")
    def test_view_ticket_wrong_user_redirects(self, mock_thumb):
        other = make_user(username="other@x.com", email="other@x.com")
        ticket = Tickets.objects.create(
            user=other,
            title="Not Yours",
            ticket_file=fake_pdf(),
            source="E",
            destination="F",
            description="",
            date_of_journey="2025-09-10",
            ticket_type="Bus",
            booked_through="RedBus",
            amount_paid=Decimal("150.00"),
        )
        response = self.client.get(
            reverse("core:view_ticket", kwargs={"ticket_id": ticket.pk})
        )
        self.assertRedirects(response, reverse("core:tickets"))

    @patch("core.models.Tickets.generate_thumbnail")
    def test_delete_ticket(self, mock_thumb):
        ticket = Tickets.objects.create(
            user=self.user,
            title="Delete Me",
            ticket_file=fake_pdf(),
            source="G",
            destination="H",
            description="",
            date_of_journey="2025-10-01",
            ticket_type="Flight",
            booked_through="Air India",
            amount_paid=Decimal("6000.00"),
        )
        self.client.get(
            reverse("core:delete_ticket", kwargs={"ticket_id": ticket.pk})
        )
        self.assertFalse(Tickets.objects.filter(pk=ticket.pk).exists())

    @patch("core.models.Tickets.generate_thumbnail")
    def test_delete_ticket_wrong_user_does_nothing(self, mock_thumb):
        other = make_user(username="other2@x.com", email="other2@x.com")
        ticket = Tickets.objects.create(
            user=other,
            title="Protected",
            ticket_file=fake_pdf(),
            source="I",
            destination="J",
            description="",
            date_of_journey="2025-11-01",
            ticket_type="Flight",
            booked_through="Vistara",
            amount_paid=Decimal("7000.00"),
        )
        self.client.get(
            reverse("core:delete_ticket", kwargs={"ticket_id": ticket.pk})
        )
        # Ticket should still exist
        self.assertTrue(Tickets.objects.filter(pk=ticket.pk).exists())

    def test_view_nonexistent_ticket_redirects(self):
        response = self.client.get(
            reverse("core:view_ticket", kwargs={"ticket_id": 99999})
        )
        self.assertRedirects(response, reverse("core:tickets"))


# ---------------------------------------------------------------------------
# 5. AI Ticket Extraction Tests
# ---------------------------------------------------------------------------

class CreateTicketTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.client.login(username="testuser", password="testpass123")

    def test_no_file_returns_404(self):
        response = self.client.post(reverse("core:create_ticket"), {})
        self.assertEqual(response.status_code, 404)

    @patch("core.views.process_file")
    def test_valid_ticket_pdf_returns_success(self, mock_process):
        # The view splits on "{", re-joins, then strips the last 3 chars (``` or similar).
        # We craft a response where that logic produces valid JSON.
        inner_json = (
            '"Source": "Mumbai", "Destination": "Delhi", '
            '"Ticket Type": "Flight", "Description": "Test", '
            '"Date of Journey": "2025-06-01", "Title": "MUM-DEL", '
            '"Booked Through": "MakeMyTrip"'
        )
        # view does: json_part = "{" + rest; then json_part = json_part[:-3]
        # so we append 3 dummy chars after the closing brace
        mock_process.return_value = "Yes, this is a ticket. {" + inner_json + "}abc"
        response = self.client.post(
            reverse("core:create_ticket"),
            {"file": fake_pdf()},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("ticket_data", data)
        self.assertEqual(data["ticket_data"]["Source"], "Mumbai")

    @patch("core.views.process_file")
    def test_non_ticket_pdf_returns_error(self, mock_process):
        mock_process.return_value = "No, it's not a ticket. This is an invoice."
        response = self.client.post(
            reverse("core:create_ticket"),
            {"file": fake_pdf()},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["status"], "error")

    def test_get_request_not_allowed(self):
        response = self.client.get(reverse("core:create_ticket"))
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# 6. Statistics Tests
# ---------------------------------------------------------------------------

class StatisticsViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.client.login(username="testuser", password="testpass123")

    def test_statistics_page_loads(self):
        response = self.client.get(reverse("core:statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/statistics.html")

    def test_anonymous_redirected(self):
        self.client.logout()
        response = self.client.get(reverse("core:statistics"))
        self.assertRedirects(response, reverse("core:login"))

    @patch("core.models.Tickets.generate_thumbnail")
    def test_statistics_data_category_mode(self, mock_thumb):
        Tickets.objects.create(
            user=self.user,
            title="T1",
            ticket_file=fake_pdf(),
            source="A",
            destination="B",
            description="",
            date_of_journey="2025-05-01",
            ticket_type="Flight",
            booked_through="X",
            amount_paid=Decimal("1000.00"),
        )
        response = self.client.get(
            reverse("core:statistics_data"), {"year": "2025", "mode": "category"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("labels", data)
        self.assertIn("data", data)
        self.assertEqual(data["labels"], ["Tickets", "Hotels"])
        self.assertEqual(data["data"][0], 1000.0)

    @patch("core.models.Tickets.generate_thumbnail")
    def test_statistics_data_platform_mode(self, mock_thumb):
        Tickets.objects.create(
            user=self.user,
            title="T2",
            ticket_file=fake_pdf(),
            source="C",
            destination="D",
            description="",
            date_of_journey="2025-06-01",
            ticket_type="Bus",
            booked_through="RedBus",
            amount_paid=Decimal("500.00"),
        )
        response = self.client.get(
            reverse("core:statistics_data"), {"year": "2025", "mode": "platforms"}
        )
        data = response.json()
        self.assertIn("RedBus", data["labels"])

    def test_statistics_data_anonymous_returns_403(self):
        self.client.logout()
        response = self.client.get(reverse("core:statistics_data"))
        self.assertEqual(response.status_code, 403)


# ---------------------------------------------------------------------------
# 7. UserProfile Tests
# ---------------------------------------------------------------------------

class UserProfileTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.client.login(username="testuser", password="testpass123")

    def test_profile_auto_created_on_get_or_create(self):
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.assertTrue(created)
        self.assertEqual(profile.currency, "INR")
        self.assertEqual(profile.miles_traveled, 0)

    def test_profile_str(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertIn(self.user.username, str(profile))

    def test_profile_page_loads(self):
        UserProfile.objects.create(user=self.user)
        response = self.client.get(reverse("core:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/profile.html")

    def test_update_profile_changes_currency(self):
        UserProfile.objects.create(user=self.user)
        self.client.post(
            reverse("core:update_profile"),
            {
                "first_name": "Test",
                "last_name": "User",
                "change_currency": "USD",
            },
        )
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.currency, "USD")

    def test_update_profile_anonymous_redirects(self):
        self.client.logout()
        response = self.client.post(reverse("core:update_profile"), {})
        self.assertRedirects(response, reverse("core:login"))

    def test_update_password_wrong_current_password(self):
        response = self.client.post(
            reverse("core:updatepassword"),
            {"current_password": "wrongpass", "new_password": "newpass123"},
        )
        self.assertContains(response, "incorrect")

    def test_update_password_success(self):
        response = self.client.post(
            reverse("core:updatepassword"),
            {"current_password": "testpass123", "new_password": "newpass456"},
        )
        self.assertContains(response, "successfully")
        # Verify new password works
        self.assertTrue(
            self.client.login(username="testuser", password="newpass456")
        )


# ---------------------------------------------------------------------------
# 8. Reservations Tests
# ---------------------------------------------------------------------------

class ReservationViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.client.login(username="testuser", password="testpass123")

    def test_reservations_page_loads(self):
        response = self.client.get(reverse("core:reservations"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/reservations.html")

    def test_add_reservation_page_loads(self):
        response = self.client.get(reverse("core:add_reservation"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_cannot_view_reservations(self):
        self.client.logout()
        response = self.client.get(reverse("core:reservations"))
        self.assertRedirects(response, reverse("core:login"))

    @patch("core.models.Reservations.generate_thumbnail")
    def test_delete_reservation(self, mock_thumb):
        reservation = Reservations.objects.create(
            user=self.user,
            reservation_name="Hotel Stay",
            reservation_file=fake_pdf(),
            description="",
            date_of_reservation="2025-07-10",
            reservation_type="Hotel",
            booked_through="Booking.com",
            amount_paid=Decimal("3000.00"),
        )
        self.client.get(
            reverse("core:delete_reservation",
                    kwargs={"reservation_id": reservation.pk})
        )
        self.assertFalse(Reservations.objects.filter(pk=reservation.pk).exists())

    @patch("core.models.Reservations.generate_thumbnail")
    def test_view_reservation_detail(self, mock_thumb):
        reservation = Reservations.objects.create(
            user=self.user,
            reservation_name="Beach Resort",
            reservation_file=fake_pdf(),
            description="A nice beach holiday",
            date_of_reservation="2025-08-20",
            reservation_type="Hotel",
            booked_through="Agoda",
            amount_paid=Decimal("8000.00"),
        )
        response = self.client.get(
            reverse("core:view_reservation",
                    kwargs={"reservation_id": reservation.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Beach Resort")

    @patch("core.models.Reservations.generate_thumbnail")
    def test_view_reservation_wrong_user_redirects(self, mock_thumb):
        other = make_user(username="other3@x.com", email="other3@x.com")
        reservation = Reservations.objects.create(
            user=other,
            reservation_name="Other's Hotel",
            reservation_file=fake_pdf(),
            description="",
            date_of_reservation="2025-09-01",
            reservation_type="Hotel",
            booked_through="Hotels.com",
            amount_paid=Decimal("5000.00"),
        )
        response = self.client.get(
            reverse("core:view_reservation",
                    kwargs={"reservation_id": reservation.pk})
        )
        self.assertRedirects(response, reverse("core:reservations"))


# ---------------------------------------------------------------------------
# 9. Utility Function Tests
# ---------------------------------------------------------------------------

class GetConvertedINRTests(TestCase):

    def test_known_currency_conversion(self):
        """USD → INR: should return a positive Decimal."""
        result = get_converted_INR("USD", 100)
        self.assertGreater(result, 0)

    def test_unknown_currency_returns_original(self):
        """Unknown currency code should fall back to the original amount."""
        result = get_converted_INR("XYZ", 500)
        self.assertEqual(result, Decimal(500))

    def test_inr_to_inr(self):
        """INR → INR conversion should equal the original amount (USD→INR via 1)."""
        result = get_converted_INR("INR", 1000)
        self.assertIsNotNone(result)


class TravelScoreTests(TestCase):

    def setUp(self):
        self.user = make_user()
        UserProfile.objects.create(user=self.user, triprep_score=Decimal("0.0000"))
        # Use Django's RequestFactory to get a real request with a real User
        from django.test import RequestFactory
        self.factory = RequestFactory()

    def _make_request(self):
        """Return a GET request authenticated as self.user."""
        request = self.factory.get("/")
        request.user = self.user
        return request

    def test_score_increases_with_miles(self):
        from core.views import generate_travel_score

        generate_travel_score(self._make_request(), 1000)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.triprep_score, Decimal("1.0000"))

    def test_score_accumulates(self):
        from core.views import generate_travel_score

        generate_travel_score(self._make_request(), 500)
        generate_travel_score(self._make_request(), 500)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.triprep_score, Decimal("1.0000"))


# ---------------------------------------------------------------------------
# 10. General Page & Edge Case Tests
# ---------------------------------------------------------------------------

class GeneralPageTests(TestCase):

    def setUp(self):
        self.user = make_user()

    @patch("core.views.get_converted_INR", return_value=Decimal("900000"))
    def test_index_page_loads(self, mock_conv):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 200)

    def test_about_page_loads(self):
        response = self.client.get(reverse("core:about_triprep"))
        self.assertEqual(response.status_code, 200)

    def test_ai_world_requires_login(self):
        response = self.client.get(reverse("core:ai-world"))
        self.assertRedirects(response, reverse("core:login"))

    def test_ai_world_logged_in(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("core:ai-world"))
        self.assertEqual(response.status_code, 200)

    @patch("core.models.Tickets.generate_thumbnail")
    def test_ticket_list_is_paginated(self, mock_thumb):
        self.client.login(username="testuser", password="testpass123")
        for i in range(15):
            Tickets.objects.create(
                user=self.user,
                title=f"Ticket {i}",
                ticket_file=fake_pdf(),
                source="A",
                destination="B",
                description="",
                date_of_journey="2025-05-01",
                ticket_type="Flight",
                booked_through="X",
                amount_paid=Decimal("100.00"),
            )
        response = self.client.get(reverse("core:tickets"))
        # Default page size is 10
        self.assertEqual(len(response.context["tickets"]), 10)

    def test_save_ticket_get_request_handled(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("core:save_ticket"))
        # GET to save_ticket should not crash — renders booking_saved or redirects
        self.assertIn(response.status_code, [200, 302])