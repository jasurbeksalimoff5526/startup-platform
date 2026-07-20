from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response

from startups.models import Startup
from shared.permissions import IsCommentOwner, IsRatingOwner

from .models import Comment, Rating
from .seralizer import CommentSerializer, RatingSerializer


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Comment.objects.filter(
                startup_id=self.kwargs["startup_id"],
                parent__isnull=True,
            )
            .select_related("author")
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        startup_id = self.kwargs["startup_id"]
        cache_key = f"startup:{startup_id}:comments"

        data = cache.get(cache_key)
        if data is not None:
            return Response(data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        cache.set(cache_key, serializer.data, timeout=60)
        cache.set("test", "hello", timeout=300)
        print("CACHE:", cache.get("test"))
        print("BACKEND:", cache.__class__)

        return Response(serializer.data)

    def perform_create(self, serializer):
        startup = get_object_or_404(
            Startup,
            pk=self.kwargs["startup_id"]
        )

        serializer.save(
            author=self.request.user,
            startup=startup
        )

        cache.delete(f"startup:{startup.id}:comments")


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.select_related("startup")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentOwner]

    def perform_update(self, serializer):
        comment = serializer.save(edited=True)

        cache.delete(
            f"startup:{comment.startup_id}:comments"
        )

    def perform_destroy(self, instance):
        startup_id = instance.startup_id

        instance.delete()

        cache.delete(
            f"startup:{startup_id}:comments"
        )


class RatingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Rating.objects.filter(
                startup_id=self.kwargs["startup_id"]
            )
            .select_related("user")
        )

    def list(self, request, *args, **kwargs):
        startup_id = self.kwargs["startup_id"]
        cache_key = f"startup:{startup_id}:ratings"

        data = cache.get(cache_key)
        if data is not None:
            return Response(data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        cache.set(cache_key, serializer.data, timeout=60)

        return Response(serializer.data)

    def perform_create(self, serializer):
        startup = get_object_or_404(
            Startup,
            pk=self.kwargs["startup_id"]
        )

        serializer.save(
            user=self.request.user,
            startup=startup
        )

        cache.delete(
            f"startup:{startup.id}:ratings"
        )


class RatingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.select_related("startup")
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated, IsRatingOwner]

    def perform_update(self, serializer):
        rating = serializer.save()

        cache.delete(
            f"startup:{rating.startup_id}:ratings"
        )

    def perform_destroy(self, instance):
        startup_id = instance.startup_id

        instance.delete()

        cache.delete(
            f"startup:{startup_id}:ratings"
        )