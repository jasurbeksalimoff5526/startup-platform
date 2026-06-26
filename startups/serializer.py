from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Category, Startup


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "created_at"]
        read_only_fields = ["id", "created_at"]


class StartupSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Startup
        fields = [
            "id",
            "owner",
            "category",
            "title",
            "slug",
            "short_description",
            "description",
            "logo",
            "website",
            "github",
            "demo",
            "stage",
            "tags",
            "views",
            "is_public",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "owner",
            "views",
            "created_at",
        ]

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise ValidationError("Startup nomi bo'sh bo'lishi mumkin emas.")

        return value

    def validate_short_description(self, value):
        value = value.strip()

        if not value:
            raise ValidationError("Qisqa tavsif kiritilishi shart.")

        return value
