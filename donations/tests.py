from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from donations.models import Donation
from startups.models import Category, Startup


class DonationApiTests(APITestCase):
    def setUp(self):
        self.donor = CustomUser.objects.create_user(
            username="donor",
            email="donor@example.com",
            password="StrongPass123!",
        )
        self.owner = CustomUser.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )
        self.category = Category.objects.create(name="AI", slug="ai")
        self.closed_startup = Startup.objects.create(
            owner=self.owner,
            category=self.category,
            title="Closed",
            slug="closed",
            short_description="Short",
            description="Long",
            is_open_source=False,
        )
        self.open_startup = Startup.objects.create(
            owner=self.owner,
            category=self.category,
            title="Open",
            slug="open",
            short_description="Short",
            description="Long",
            is_open_source=True,
        )

    def test_donation_blocked_when_not_open_source(self):
        self.client.force_authenticate(self.donor)
        response = self.client.post(
            f"/donations/startups/{self.closed_startup.id}/donations/",
            {"amount": "50.00", "message": "support"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Donation.objects.count(), 0)

    def test_donation_allowed_when_open_source(self):
        self.client.force_authenticate(self.donor)
        response = self.client.post(
            f"/donations/startups/{self.open_startup.id}/donations/",
            {"amount": "75.50", "message": "great work"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        donation = Donation.objects.get()
        self.assertEqual(donation.donor, self.donor)
        self.assertEqual(donation.startup, self.open_startup)
        self.assertEqual(str(donation.amount), "75.50")

    def test_donation_rejects_zero_amount(self):
        self.client.force_authenticate(self.donor)
        response = self.client.post(
            f"/donations/startups/{self.open_startup.id}/donations/",
            {"amount": "0", "message": ""},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
