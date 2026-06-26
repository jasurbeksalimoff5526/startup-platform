from django.db import models

from accounts.models import CustomUser
from shared.models import BaseModel


class FailureReason(BaseModel):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class FailedStartup(BaseModel):
    author = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="failed_startups")
    failure_reason = models.ForeignKey(FailureReason,on_delete=models.SET_NULL,null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    months_worked = models.PositiveIntegerField()
    money_spent = models.DecimalField(max_digits=12, decimal_places=2)
    lesson_learned = models.TextField()

    def __str__(self):
        return self.title
