from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Comment, Rating


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment

        fields = [
            "id",
            "startup",
            "author",
            "parent",
            "content",
            "edited",
            "replies",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "startup",
            "author",
            "edited",
            "created_at",
        ]

    def get_replies(self, obj):
        return CommentSerializer(
            obj.replies.all(),
            many=True
        ).data

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise ValidationError(
                "Comment bo'sh bo'lishi mumkin emas."
            )

        return value


class RatingSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField(
        read_only=True
    )

    average = serializers.SerializerMethodField()

    class Meta:
        model = Rating

        fields = [
            "id",

            "startup",

            "user",

            "problem",

            "market",

            "competition",

            "monetization",

            "execution",

            "average",

            "created_at",
        ]

        read_only_fields = [
            "id",
            "startup",

            "user",

            "average",

            "created_at",
        ]

    def get_average(self, obj):

        return round(

            (
                obj.problem +

                obj.market +

                obj.competition +

                obj.monetization +

                obj.execution

            ) / 5,

            2

        )

    def validate(self, attrs):
        for field in ("problem", "market", "competition", "monetization", "execution"):
            value = attrs.get(field)
            if value is not None and not 1 <= value <= 5:
                raise ValidationError({field: "Baholash 1 dan 5 gacha bo'lishi kerak."})
        return attrs
