from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import MESSAGE, Notification
from notifications.services import create_notification
from startups.models import Startup
from .models import ChatMessage
from .serializers import ChatMessageSerializer


class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class StartupMessageListCreateAPIView(ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        startup = get_object_or_404(Startup, pk=self.kwargs["startup_id"])
        return ChatMessage.objects.filter(startup=startup).select_related("sender").order_by("created_at")

    def create(self, request, *args, **kwargs):
        startup = get_object_or_404(Startup, pk=self.kwargs["startup_id"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = ChatMessage.objects.create(
            startup=startup,
            sender=request.user,
            text=serializer.validated_data["text"],
        )
        self._notify_owner(startup, request.user)
        output = self.get_serializer(message)
        return Response(output.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _notify_owner(startup, sender):
        recipient = startup.owner
        if recipient is None or getattr(recipient, "id", None) == sender.id:
            return
        already_unread = Notification.objects.filter(
            receiver=recipient,
            startup=startup,
            notification_type=MESSAGE,
            is_read=False,
        ).exists()
        if not already_unread:
            create_notification(
                receiver=recipient,
                sender=sender,
                notification_type=MESSAGE,
                startup=startup,
            )


class StartupMessageListAPIView(ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        startup = get_object_or_404(Startup, pk=self.kwargs["startup_id"])
        return ChatMessage.objects.filter(startup=startup).select_related("sender").order_by("created_at")
