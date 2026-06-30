from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    Application,
    Bookmark,
    Category,
    Startup,
    Vacancy,
)


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
            "is_open_source",
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


class BookmarkSerializer(serializers.ModelSerializer):
    startup_id = serializers.UUIDField()

    class Meta:
        model = Bookmark
        fields = ["id", "startup", "startup_id", "created_at"]
        read_only_fields = ["id", "startup", "created_at"]

    def validate(self, attrs):
        startup_id = attrs.get("startup_id")
        try:
            attrs["startup"] = Startup.objects.get(pk=startup_id)
        except Startup.DoesNotExist:
            raise ValidationError({"startup_id": "Bunday startup mavjud emas."})
        return attrs


class VacancySerializer(serializers.ModelSerializer):
    startup_title = serializers.CharField(source="startup.title", read_only=True)

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "startup",
            "startup_title",
            "title",
            "role",
            "description",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "startup", "startup_title", "status", "created_at"]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise ValidationError("Vakansiya nomi bo'sh bo'lishi mumkin emas.")
        return value

    def validate_description(self, value):
        value = value.strip()
        if not value:
            raise ValidationError("Vakansiya tavsifi bo'sh bo'lishi mumkin emas.")
        return value


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.StringRelatedField(read_only=True)
    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy",
            "vacancy_title",
            "applicant",
            "message",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "vacancy_title", "applicant", "status", "created_at"]
