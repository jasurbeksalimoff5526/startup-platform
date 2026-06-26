from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.models import FOUNDER, MENTOR


class IsFounder(BasePermission):
    """
    Faqat founderlar POST, PUT, PATCH, DELETE qila oladi.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == FOUNDER
        )


class IsMentor(BasePermission):
    """
    Faqat mentorlar uchun.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == MENTOR
        )


class IsFounderOrReadOnly(BasePermission):
    """
    Hamma o'qiy oladi.
    Faqat founder yozishi mumkin.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == FOUNDER
        )


class IsStartupOwner(BasePermission):
    """
    Startup egasi tahrirlashi yoki o'chirishi mumkin.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and obj.owner == request.user
        )


class IsCommentOwner(BasePermission):
    """
    Komment egasi tahrirlashi yoki o'chirishi mumkin.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and obj.author == request.user
        )


class IsRatingOwner(BasePermission):
    """
    Rating egasi tahrirlashi yoki o'chirishi mumkin.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and obj.user == request.user
        )


class IsFailedStartupOwner(BasePermission):
    """
    Failed Startup posti egasi.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and obj.author == request.user
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Egasi yoki admin tahrirlashi mumkin.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and (
                obj.owner == request.user
                or request.user.is_admin
            )
        )
