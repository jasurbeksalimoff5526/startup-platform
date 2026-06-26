from rest_framework import status
from rest_framework.test import APITestCase


class RegisterTests(APITestCase):
    def test_register_cannot_create_admin_role(self):
        response = self.client.post(
            "/auth/register",
            {
                "username": "adminish",
                "email": "adminish@example.com",
                "password": "StrongPass123!",
                "role": "admin",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
