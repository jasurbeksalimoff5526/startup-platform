from rest_framework.test import APITestCase

from accounts.models import CustomUser
from chat.models import ChatMessage
from notifications.models import MESSAGE, Notification
from startups.models import Category, Startup


class ChatApiTests(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )
        self.sender = CustomUser.objects.create_user(
            username="sender",
            email="sender@example.com",
            password="StrongPass123!",
        )
        self.category = Category.objects.create(name="SaaS", slug="saas")
        self.startup = Startup.objects.create(
            owner=self.owner,
            category=self.category,
            title="Alpha",
            slug="alpha",
            short_description="Short",
            description="Long",
        )

    def test_post_message_creates_record_and_notification(self):
        self.client.force_authenticate(self.sender)
        response = self.client.post(
            f"/chat/startups/{self.startup.id}/messages/",
            {"text": "hello"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        message = ChatMessage.objects.get()
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.startup, self.startup)
        self.assertEqual(message.text, "hello")
        self.assertTrue(
            Notification.objects.filter(
                receiver=self.owner,
                sender=self.sender,
                startup=self.startup,
                notification_type=MESSAGE,
            ).exists()
        )

    def test_post_message_rejects_empty_text(self):
        self.client.force_authenticate(self.sender)
        response = self.client.post(
            f"/chat/startups/{self.startup.id}/messages/",
            {"text": "   "},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ChatMessage.objects.count(), 0)
