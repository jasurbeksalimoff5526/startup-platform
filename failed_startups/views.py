from rest_framework import generics, permissions
from .models import FailureReason, FailedStartup
from .serializers import FailureReasonSerializer, FailedStartupSerializer
from shared.permissions import IsFailedStartupOwner


class FailureReasonListAPIView(generics.ListAPIView):
    queryset = FailureReason.objects.all()
    serializer_class = FailureReasonSerializer
    permission_classes = [permissions.IsAuthenticated]


class FailedStartupListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FailedStartupSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FailedStartup.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FailedStartupDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FailedStartup.objects.all()
    serializer_class = FailedStartupSerializer
    permission_classes = [permissions.IsAuthenticated, IsFailedStartupOwner]
