import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from notifications.models import MESSAGE, Notification
from notifications.services import create_notification
from startups.models import Startup
from .models import ChatMessage

MAX_MESSAGE_LENGTH = 5000


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        self.startup_id = str(self.scope["url_route"]["kwargs"]["startup_id"])

        if self.user is None or self.user.is_anonymous:
            await self.close(code=4001)
            return

        self.startup = await self.get_startup(self.startup_id)
        if self.startup is None:
            await self.close(code=4004)
            return

        self.group_name = f"startup_chat_{self.startup_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if not text_data:
            return
        try:
            content = await self.decode_json(text_data)
        except (json.JSONDecodeError, ValueError):
            await self.send_json({"type": "error", "detail": "Invalid JSON."})
            return
        await self.receive_json(content, **kwargs)

    async def receive_json(self, content, **kwargs):
        if not isinstance(content, dict):
            await self.send_json({"type": "error", "detail": "Invalid message format."})
            return
        msg_type = content.get("type")
        if msg_type == "message":
            await self.handle_message(content)
        elif msg_type == "typing":
            await self.handle_typing()
        elif msg_type == "read":
            await self.handle_read()
        else:
            await self.send_json({"type": "error", "detail": "Unknown message type."})

    async def handle_message(self, content):
        text = content.get("text")
        if not isinstance(text, str) or not text.strip():
            await self.send_json({"type": "error", "detail": "Message bo'sh bo'lishi mumkin emas."})
            return
        text = text.strip()
        if len(text) > MAX_MESSAGE_LENGTH:
            await self.send_json({"type": "error", "detail": "Message juda uzun."})
            return

        message = await self.create_message(text)
        await self.channel_layer.group_send(self.group_name, {
            "type": "chat.message",
            "id": str(message.id),
            "sender": self.user.username,
            "sender_id": str(self.user.id),
            "text": message.text,
            "created_at": message.created_at.isoformat(),
        })
        await self.notify_recipient()

    async def handle_typing(self):
        await self.channel_layer.group_send(self.group_name, {
            "type": "chat.typing",
            "user": self.user.username,
            "sender_channel": self.channel_name,
        })

    async def handle_read(self):
        read_at = await self.mark_read()
        if read_at is None:
            return
        await self.channel_layer.group_send(self.group_name, {
            "type": "chat.read",
            "user": self.user.username,
            "read_at": read_at.isoformat(),
        })

    async def chat_read(self, event):
        if event["user"] == self.user.username:
            return
        await self.send_json({
            "type": "read",
            "user": event["user"],
            "read_at": event["read_at"],
        })

    @database_sync_to_async
    def mark_read(self):
        now = timezone.now()
        updated = (
            ChatMessage.objects.filter(startup=self.startup, is_read=False)
            .exclude(sender=self.user)
            .update(is_read=True, read_at=now)
        )
        Notification.objects.filter(
            receiver=self.user,
            startup=self.startup,
            notification_type=MESSAGE,
            is_read=False,
        ).update(is_read=True)
        return now if updated else None

    async def chat_typing(self, event):
        if event.get("sender_channel") == self.channel_name:
            return
        await self.send_json({"type": "typing", "user": event["user"]})

    async def chat_message(self, event):
        await self.send_json({
            "type": "message",
            "id": event["id"],
            "sender": event["sender"],
            "sender_id": event["sender_id"],
            "text": event["text"],
            "created_at": event["created_at"],
            "is_read": False,
        })

    @database_sync_to_async
    def get_startup(self, startup_id):
        return Startup.objects.select_related("owner").filter(pk=startup_id).first()

    @database_sync_to_async
    def create_message(self, text):
        return ChatMessage.objects.create(startup=self.startup, sender=self.user, text=text)

    @database_sync_to_async
    def notify_recipient(self):
        recipient = self.startup.owner
        if recipient_id := getattr(recipient, "id", None):
            if recipient_id == self.user.id:
                return
        already_unread = Notification.objects.filter(
            receiver=recipient,
            startup=self.startup,
            notification_type=MESSAGE,
            is_read=False,
        ).exists()
        if not already_unread:
            create_notification(
                receiver=recipient,
                sender=self.user,
                notification_type=MESSAGE,
                startup=self.startup,
            )
