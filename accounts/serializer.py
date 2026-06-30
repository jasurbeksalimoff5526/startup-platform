from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from .models import CustomUser
from .profiles import InvestorProfile, MentorProfile


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Register Example",
            value={
                "username": "username",
                "email": "email@gmail.com",
                "password": "parol111",
                "bio": "Backend developer",
            },
            request_only=True,
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
            "phone_number",
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
            "phone_number",
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
        read_only_fields = ["id", "is_verified", "created_at"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user:
            raise ValidationError({"message": "Authentication required"})

        if attrs["new_password"] != attrs["confirm_password"]:
            raise ValidationError(
                {"confirm_password": "Parollar bir-biriga mos kelmadi!"}
            )

        if not user.check_password(attrs["old_password"]):
            raise ValidationError({"old_password": "Eski parol noto'g'ri"})

        attrs["user"] = user
        return attrs


class MentorProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = MentorProfile
        fields = [
            "id",
            "username",
            "email",
            "expertise",
            "years_of_experience",
            "available",
            "hourly_rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "username", "email", "created_at", "updated_at"]

    def validate_years_of_experience(self, value):
        if value < 0:
            raise ValidationError("Tajriba yili manfiy bo'lishi mumkin emas.")
        return value

    def validate_hourly_rate(self, value):
        if value < 0:
            raise ValidationError("Soatlik tarif manfiy bo'lishi mumkin emas.")
        return value


class InvestorProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = InvestorProfile
        fields = [
            "id",
            "username",
            "email",
            "company",
            "bio",
            "min_ticket",
            "max_ticket",
            "industries",
            "countries",
            "verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "verified",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        min_ticket = attrs.get("min_ticket", 0)
        max_ticket = attrs.get("max_ticket", 0)
        if min_ticket is not None and min_ticket < 0:
            raise ValidationError("min_ticket manfiy bo'lishi mumkin emas.")
        if max_ticket is not None and max_ticket < 0:
            raise ValidationError("max_ticket manfiy bo'lishi mumkin emas.")
        if min_ticket and max_ticket and min_ticket > max_ticket:
            raise ValidationError(
                {"max_ticket": "max_ticket min_ticket dan kichik bo'lishi mumkin emas."}
            )
        return attrs
