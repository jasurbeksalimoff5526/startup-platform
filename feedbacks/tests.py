from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import FOUNDER, USER, CustomUser
from feedbacks.models import Comment, Rating
from startups.models import Category, Startup


class FeedbackPermissionTests(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
            role=FOUNDER,
        )
        self.author = CustomUser.objects.create_user(
            username="author",
            email="author@example.com",
            password="StrongPass123!",
            role=USER,
        )
        self.other = CustomUser.objects.create_user(
            username="other",
            email="other@example.com",
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
        )
        self.other_startup = Startup.objects.create(
            owner=self.owner,
            category=self.category,
            title="Beta",
            slug="beta",
            short_description="Short",
            description="Long",
        )

    def test_comment_create_uses_url_startup_and_non_owner_cannot_delete(self):
        self.client.force_authenticate(self.author)
        response = self.client.post(
            f"/feedbacks/startup/{self.startup.id}/comments/",
            {"startup": str(self.other_startup.id), "content": "Nice"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get()
        self.assertEqual(comment.startup, self.startup)

        self.client.force_authenticate(self.other)
        response = self.client.delete(f"/feedbacks/comments/{comment.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rating_owner_only_and_range_validation(self):
        self.client.force_authenticate(self.author)
        response = self.client.post(
            f"/feedbacks/startup/{self.startup.id}/ratings/",
            {
                "problem": 6,
                "market": 5,
                "competition": 5,
                "monetization": 5,
                "execution": 5,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        rating = Rating.objects.create(
            startup=self.startup,
            user=self.author,
            problem=5,
            market=5,
            competition=5,
            monetization=5,
            execution=5,
        )

        self.client.force_authenticate(self.other)
        response = self.client.patch(f"/feedbacks/ratings/{rating.id}/", {"problem": 1}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
