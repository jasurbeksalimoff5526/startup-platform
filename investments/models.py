from django.db import models

from accounts.models import CustomUser
from shared.models import BaseModel
from startups.models import Startup


class Investment(BaseModel):
    INVESTMENT_STATUS_PENDING = "pending"
    INVESTMENT_STATUS_CONFIRMED = "confirmed"
    INVESTMENT_STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (INVESTMENT_STATUS_PENDING, "Pending"),
        (INVESTMENT_STATUS_CONFIRMED, "Confirmed"),
        (INVESTMENT_STATUS_REJECTED, "Rejected"),
    )

    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="investments")
    investor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="investments")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=INVESTMENT_STATUS_PENDING)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["startup", "-created_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["investor", "startup"],
                name="unique_investor_startup",
            )
        ]

    def __str__(self):
        return f"{self.investor} -> {self.startup}: {self.amount}"
