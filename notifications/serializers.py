from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    sender_name = serializers.SerializerMethodField()
    startup_title = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification

        fields = [
            "id",
            "receiver",
            "sender",
            "sender_name",
            "startup",
            "startup_title",
            "notification_type",
            "message",
            "is_read",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "receiver",
            "sender",
            "sender_name",
            "startup",
            "startup_title",
            "notification_type",
            "message",
            "created_at",
        ]

    def get_sender_name(self, obj):
        return obj.sender.username

    def get_startup_title(self, obj):
        return obj.startup.title if obj.startup else None

    def get_message(self, obj):

        if obj.notification_type == "comment":
            return f"{obj.sender.username} commented on your startup"

        elif obj.notification_type == "follow":
            return f"{obj.sender.username} followed you"

        elif obj.notification_type == "bookmark":
            return f"{obj.sender.username} bookmarked your startup"

        elif obj.notification_type == "message":
            return f"{obj.sender.username} sent a message about your startup"

        return ""
