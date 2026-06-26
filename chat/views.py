from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from startups.models import Startup
from .models import ChatMessage
from .serializers import ChatMessageSerializer


class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class StartupMessageListAPIView(ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        startup = get_object_or_404(Startup, pk=self.kwargs["startup_id"])
        return ChatMessage.objects.filter(startup=startup).select_related("sender").order_by("created_at")
