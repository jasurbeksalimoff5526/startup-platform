from django.urls import path

from .views import (
    CommentListCreateAPIView,
    CommentDetailAPIView,
    RatingListCreateAPIView,
    RatingDetailAPIView,
)

urlpatterns = [
    path("startups/<uuid:startup_id>/comments/", CommentListCreateAPIView.as_view(), name="feedback-comments"),
    path("comments/<uuid:pk>/", CommentDetailAPIView.as_view(), name="feedback-comment-detail"),
    path("startups/<uuid:startup_id>/ratings/", RatingListCreateAPIView.as_view(), name="feedback-ratings"),
    path("ratings/<uuid:pk>/", RatingDetailAPIView.as_view(), name="feedback-rating-detail"),
]
