from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import FOUNDER, USER, CustomUser
from startups.models import Category, Startup


class StartupApiTests(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
            role=FOUNDER,
        )
        self.other = CustomUser.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass123!",
            role=FOUNDER,
        )
        self.user = CustomUser.objects.create_user(
            username="user",
            email="user@example.com",
            password="StrongPass123!",
            role=USER,
        )
        self.category = Category.objects.create(name="AI", slug="ai")
        self.startup = Startup.objects.create(
            owner=self.owner,
            category=self.category,
            title="Alpha",
            slug="alpha",
            short_description="Short",
            description="Long",
            is_public=True,
        )

    def test_category_create_exists_for_founder(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            "/startups/categories/",
            {"name": "Fintech", "slug": "fintech"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(slug="fintech").exists())

    def test_startup_detail_uses_uuid_pk_and_non_owner_cannot_patch(self):
        detail_url = f"/startups/{self.startup.id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.other)
        response = self.client.patch(detail_url, {"title": "Changed"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.startup.refresh_from_db()
        self.assertEqual(self.startup.title, "Alpha")

    def test_private_startup_is_hidden_from_other_users(self):
        self.startup.is_public = False
        self.startup.save(update_fields=["is_public"])

        self.client.force_authenticate(self.user)
        response = self.client.get(f"/startups/{self.startup.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
