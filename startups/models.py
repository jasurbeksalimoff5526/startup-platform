from django.db import models
from accounts.models import CustomUser
from shared.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


IDEA = "idea"
MVP = "mvp"
BETA = "beta"
LAUNCHED = "launched"
CLOSED = "closed"


class Startup(BaseModel):
    STAGE_CHOICES = (
        (IDEA, "Idea"),
        (MVP, "MVP"),
        (BETA, "Beta"),
        (LAUNCHED, "Launched"),
        (CLOSED, "Closed"),
    )

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="startups")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="startups")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    logo = models.ImageField(upload_to="startup/logo/", blank=True, null=True)
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    demo = models.URLField(blank=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default=IDEA)
    tags = models.ManyToManyField(Tag, blank=True, related_name="startups")
    views = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class StartupImage(BaseModel):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="startup/images/")


class Bookmark(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bookmarks")
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="bookmarks")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "startup"],
                name="unique_bookmark"
            )
        ]
