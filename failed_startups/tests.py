from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from failed_startups.models import FailedStartup, FailureReason


class FailedStartupPermissionTests(APITestCase):
    def test_non_owner_cannot_delete_failed_startup(self):
        author = CustomUser.objects.create_user(
            username="author",
            email="author@example.com",
            password="StrongPass123!",
        )
        other = CustomUser.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass123!",
        )
        reason = FailureReason.objects.create(title="No market")
        failed_startup = FailedStartup.objects.create(
            author=author,
            failure_reason=reason,
            title="Miss",
            description="Failed",
            months_worked=3,
            money_spent="100.00",
            lesson_learned="Validate first",
        )

        self.client.force_authenticate(other)
        response = self.client.delete(f"/failed_startups/{failed_startup.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
