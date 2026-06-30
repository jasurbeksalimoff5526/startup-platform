from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from startups.models import Startup
from .models import Donation
from .serializers import DonationSerializer
from rest_framework.exceptions import PermissionDenied

class StartupDonationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Donation.objects.filter(
            startup_id=self.kwargs["startup_id"]
        ).select_related("donor").order_by("-created_at")

    def perform_create(self, serializer):
        startup = get_object_or_404(Startup, pk=self.kwargs["startup_id"])
        if not startup.is_open_source:

            raise PermissionDenied(
                "Donation faqat ochiq kodli (open source) startaplar uchun ruxsat berilgan."
            )
        serializer.save(donor=self.request.user, startup=startup)
