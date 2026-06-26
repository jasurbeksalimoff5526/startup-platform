from django.db import models

from accounts.models import CustomUser
from shared.models import BaseModel
from startups.models import Startup


class ChatMessage(BaseModel):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="chat_messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="chat_messages")
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["startup", "created_at"])]

    def __str__(self):
        return f"{self.sender} @ {self.startup_id}: {self.text[:30]}"
