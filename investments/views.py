from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError

from startups.models import Startup
from .models import Investment
from .serializers import InvestmentSerializer


class IsInvestor(permissions.BasePermission):
    message = "Investitsiya qilish uchun InvestorProfile kerak."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(request.user, "investor_profile")


class StartupInvestmentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InvestmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsInvestor]

    def get_queryset(self):
        return (
            Investment.objects.filter(startup_id=self.kwargs["startup_id"])
            .select_related("investor")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        startup = get_object_or_404(Startup, pk=self.kwargs["startup_id"])
        if startup.owner_id == self.request.user.id:
            raise PermissionDenied("Owner o'z start-upiga investitsiya qila olmaydi.")
        if Investment.objects.filter(
            startup=startup, investor=self.request.user
        ).exists():
            raise ValidationError(
                {"non_field_errors": ["Bu start-upga allaqachon investitsiya qilgansiz."]}
            )
        try:
            with transaction.atomic():
                serializer.save(investor=self.request.user, startup=startup)
        except IntegrityError:
            raise ValidationError(
                {"non_field_errors": ["Bu start-upga allaqachon investitsiya qilgansiz."]}
            )
