from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from .models import FOUNDER, USER, MENTOR, ADMIN, CustomUser
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from rest_framework import serializers


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Register Example",
            value={
                "username": "jasur",
                "email": "jasur@gmail.com",
                "password": "parol111",
                "role": "founder",
                "bio": "Backend developer"
            },
            request_only=True
        )
    ]
)



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
            "avatar",
            "bio",
            "location",
            "company",
            "website",
            "github",
            "linkedin",
            "twitter",
        ]
        read_only_fields = ["id"]

    def validate_role(self, value):
        if value not in (FOUNDER, USER, MENTOR):
            raise ValidationError("Role FOUNDER, USER yoki MENTOR bo'lishi kerak.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["tokens"] = instance.token()
        return data


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs["username_or_email"].strip()
        password = attrs["password"]

        username = username_or_email
        if "@" in username_or_email:
            user = CustomUser.objects.filter(email__iexact=username_or_email).first()
            username = user.username if user else username_or_email

        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError({"message": "Login yoki parol noto'g'ri."})

        attrs["user"] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "role",
            "avatar",
            "bio",
            "location",
            "company",
            "website",
            "github",
            "linkedin",
            "twitter",
            "is_verified",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "role",
            "is_verified",
            "created_at",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user:
            raise ValidationError({"message": "Authentication required"})

        if attrs["new_password"] != attrs["confirm_password"]:
            raise ValidationError({"confirm_password": "Parollar bir-biriga mos kelmadi!"})

        if not user.check_password(attrs["old_password"]):
            raise ValidationError({"old_password": "Eski parol noto'g'ri"})

        attrs["user"] = user
        return attrs
