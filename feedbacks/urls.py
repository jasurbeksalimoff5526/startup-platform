from django.urls import path

from .views import (
    CommentListCreateAPIView,
    CommentDetailAPIView,
    RatingListCreateAPIView,
    RatingDetailAPIView,
)

urlpatterns = [
    path("startup/<uuid:startup_id>/comments/", CommentListCreateAPIView.as_view()),
    path("comments/<uuid:pk>/", CommentDetailAPIView.as_view()),
    path("startup/<uuid:startup_id>/ratings/", RatingListCreateAPIView.as_view()),
    path("ratings/<uuid:pk>/", RatingDetailAPIView.as_view()),
]