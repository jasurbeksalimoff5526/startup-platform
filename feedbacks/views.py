from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from .models import Comment, Rating
from .seralizer import CommentSerializer, RatingSerializer
from startups.models import Startup
from shared.permissions import IsCommentOwner, IsRatingOwner


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(startup_id=self.kwargs["startup_id"])

    def perform_create(self, serializer):
        startup = get_object_or_404(Startup, pk=self.kwargs["startup_id"])
        serializer.save(author=self.request.user, startup=startup)


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentOwner]

    def perform_update(self, serializer):
        serializer.save(edited=True)


class RatingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(startup_id=self.kwargs["startup_id"])

    def perform_create(self, serializer):
        startup = get_object_or_404(Startup, pk=self.kwargs["startup_id"])
        serializer.save(user=self.request.user, startup=startup)


class RatingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated, IsRatingOwner]
