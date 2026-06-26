from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from accounts.models import CustomUser
from shared.models import BaseModel
from startups.models import Startup


class Comment(BaseModel):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies"
    )

    content = models.TextField()
    edited = models.BooleanField(default=False)

    def __str__(self):
        return self.author.username


class Rating(BaseModel):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    problem = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    market = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    competition = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    monetization = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    execution = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "startup"],
                name="unique_rating"
            )
        ]
