from rest_framework import serializers

from .models import ChatMessage


MAX_MESSAGE_LENGTH = 5000


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    sender_id = serializers.UUIDField(source="sender.id", read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "startup",
            "sender",
            "sender_id",
            "text",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "startup", "sender", "sender_id", "is_read", "read_at", "created_at"]

    def validate_text(self, value):
        text = (value or "").strip()
        if not text:
            raise serializers.ValidationError("Message bo'sh bo'lishi mumkin emas.")
        if len(text) > MAX_MESSAGE_LENGTH:
            raise serializers.ValidationError("Message juda uzun.")
        return text
