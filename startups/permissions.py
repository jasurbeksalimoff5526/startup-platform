from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import FOUNDER


class IsFounder(BasePermission):
    """User has at least one Founder membership in StartupMember."""

    message = "Bu amal faqat Founder rolidagi foydalanuvchilar uchun ruxsat berilgan."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        from .models import StartupMember
        return StartupMember.objects.filter(user=request.user, role=FOUNDER).exists()


class IsStartupFounder(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and obj.members.filter(
                user=request.user,
                role=FOUNDER
            ).exists()
        )


class IsVacancyOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                obj.startup.members.filter(
                    user=request.user, role=FOUNDER
                ).exists()
                or request.user.is_staff
            )
        )


class IsApplicationOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                obj.applicant == request.user
                or obj.vacancy.startup.members.filter(
                    user=request.user, role=FOUNDER
                ).exists()
                or request.user.is_staff
            )
        )
