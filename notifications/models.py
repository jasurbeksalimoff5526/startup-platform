from django.db import models
from accounts.models import CustomUser
from shared.models import BaseModel
from startups.models import Startup

COMMENT = "comment"
FOLLOW = "follow"
BOOKMARK = "bookmark"
MESSAGE = "message"


class Notification(BaseModel):
    TYPE_CHOICES = (
        (COMMENT, "Comment"),
        (FOLLOW, "Follow"),
        (BOOKMARK, "Bookmark"),
        (MESSAGE, "Message"),
    )

    receiver = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="notifications")
    sender = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
