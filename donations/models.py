from django.db import models
from accounts.models import CustomUser
from shared.models import BaseModel
from startups.models import Startup


class Donation(BaseModel):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="donations")
    donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="donations")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["startup", "-created_at"])]

    def __str__(self):
        return f"{self.donor} -> {self.startup}: {self.amount}"
