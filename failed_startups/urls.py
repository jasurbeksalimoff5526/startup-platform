from django.urls import path

from .views import (
    FailedStartupDetailAPIView,
    FailedStartupListCreateAPIView,
    FailureReasonListAPIView,
)


urlpatterns = [
    path("reasons/", FailureReasonListAPIView.as_view(), name="failure-reasons"),
    path("", FailedStartupListCreateAPIView.as_view(), name="failed-startup-list-create"),
    path("<uuid:pk>/", FailedStartupDetailAPIView.as_view(), name="failed-startup-detail"),
]
