from rest_framework import serializers
from .models import FailureReason, FailedStartup


class FailureReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailureReason
        fields = ["id", "title"]
        read_only_fields = ["id"]


class FailedStartupSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FailedStartup
        fields = [
            "id",
            "author",
            "failure_reason",
            "title",
            "description",
            "months_worked",
            "money_spent",
            "lesson_learned",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "author",
            "created_at",
        ]

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Title bo'sh bo'lishi mumkin emas."
            )

        return value

    def validate_months_worked(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Oylar soni 0 dan katta bo'lishi kerak."
            )

        return value