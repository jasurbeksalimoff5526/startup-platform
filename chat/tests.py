from django.conf import settings
from django.test import TestCase

from accounts.models import FOUNDER, CustomUser
from chat.models import ChatMessage
from startups.models import Category, Startup


class ChatConfigTests(TestCase):
    def test_chat_model_and_asgi_import(self):
        owner = CustomUser.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
            role=FOUNDER,
        )
        category = Category.objects.create(name="SaaS", slug="saas")
        startup = Startup.objects.create(
            owner=owner,
            category=category,
            title="Alpha",
            slug="alpha",
            short_description="Short",
            description="Long",
        )

        message = ChatMessage.objects.create(startup=startup, sender=owner, text="hello")

        self.assertEqual(message.startup, startup)
        self.assertEqual(message.sender, owner)
        self.assertEqual(message.text, "hello")
        self.assertEqual(settings.ASGI_APPLICATION, "main.asgi.application")

        from main.asgi import application

        self.assertIsNotNone(application)
