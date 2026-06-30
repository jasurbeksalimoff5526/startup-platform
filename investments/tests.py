from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from accounts.profiles import InvestorProfile
from investments.models import Investment
from startups.models import Category, Startup


class InvestmentApiTests(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )
        self.investor = CustomUser.objects.create_user(
            username="investor",
            email="investor@example.com",
            password="StrongPass123!",
        )
        InvestorProfile.objects.create(user=self.investor)
        self.outsider = CustomUser.objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="StrongPass123!",
        )
        self.category = Category.objects.create(name="AI", slug="ai")
        self.startup = Startup.objects.create(
            owner=self.owner,
            category=self.category,
            title="Alpha",
            slug="alpha",
            short_description="Short",
            description="Long",
        )

    def test_only_investor_profile_can_invest(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.post(
            f"/investments/startups/{self.startup.id}/investments/",
            {"amount": "1000.00", "note": ""},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Investment.objects.count(), 0)

    def test_investor_can_create_and_list(self):
        self.client.force_authenticate(self.investor)
        response = self.client.post(
            f"/investments/startups/{self.startup.id}/investments/",
            {"amount": "5000.00", "note": "excited"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Investment.objects.count(), 1)

        response = self.client.get(f"/investments/startups/{self.startup.id}/investments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_cannot_invest_in_own_startup(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            f"/investments/startups/{self.startup.id}/investments/",
            {"amount": "1000.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_investment_is_blocked(self):
        Investment.objects.create(startup=self.startup, investor=self.investor, amount="100")
        self.client.force_authenticate(self.investor)
        response = self.client.post(
            f"/investments/startups/{self.startup.id}/investments/",
            {"amount": "200"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
