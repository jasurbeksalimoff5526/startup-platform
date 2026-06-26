from django.urls import path
from .views import FailureReasonListAPIView, FailedStartupListCreateAPIView, FailedStartupDetailAPIView

urlpatterns = [
    path("reasons/", FailureReasonListAPIView.as_view(), ),
    path("", FailedStartupListCreateAPIView.as_view(), ),
    path("<uuid:pk>/", FailedStartupDetailAPIView.as_view(), ),
]
