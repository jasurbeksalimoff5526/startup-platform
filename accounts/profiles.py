from django.db import models
from accounts.models import CustomUser
from shared.models import BaseModel


class MentorProfile(BaseModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="mentor_profile")
    expertise = models.CharField(max_length=255)
    years_of_experience = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username


class InvestorProfile(BaseModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="investor_profile"
    )
    company = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    min_ticket = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    max_ticket = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0)
    industries = models.JSONField(default=list)
    countries = models.JSONField(default=list)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
