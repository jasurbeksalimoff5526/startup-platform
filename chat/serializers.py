from rest_framework import serializers

from .models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    sender_id = serializers.UUIDField(source="sender.id", read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "startup", "sender", "sender_id", "text", "is_read", "read_at", "created_at"]
        read_only_fields = fields
