from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from shared.models import BaseModel


class CustomUser(AbstractUser, BaseModel):
    phone_number = models.CharField(max_length=13, blank=True, default="")
    email = models.EmailField(unique=True)
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
