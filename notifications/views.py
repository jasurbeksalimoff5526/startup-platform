from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer
# Create your views here.


class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            receiver=self.request.user
        ).order_by("-created_at")


class UnreadNotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            receiver=self.request.user,
            is_read=False
        ).order_by("-created_at")


class MarkNotificationAsReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk,receiver=request.user)
        except Notification.DoesNotExist:
            return Response(
                {"detail": "Bildirishnoma topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response(
            {"detail": "Bildirishnoma o'qilgan deb belgilandi"},
            status=status.HTTP_200_OK
        )


class MarkAllNotificationsAsReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        Notification.objects.filter(
            receiver=request.user,
            is_read=False
        ).update(is_read=True)

        return Response(
            {"detail": "Barcha bildirishnomalar o'qilgan deb belgilandi"},
            status=status.HTTP_200_OK
        )


class UnreadNotificationCountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()

        return Response({"unread_count": count})
    
