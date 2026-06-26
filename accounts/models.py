from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import BaseModel


FOUNDER = "founder"
USER = "user"
MENTOR = "mentor"
ADMIN = "admin"


class CustomUser(AbstractUser, BaseModel):
    ROLE_CHOICES = (
        (FOUNDER, "Founder"),
        (USER, "User"),
        (MENTOR, "Mentor"),
        (ADMIN, "Admin"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=USER)
    avatar = models.ImageField(upload_to="users/avatar/", blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)


    def __str__(self):
        return self.username

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @property
    def is_founder(self):
        return self.role == FOUNDER

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_mentor(self):
        return self.role == MENTOR

    @property
    def is_admin(self):
        return self.role == ADMIN