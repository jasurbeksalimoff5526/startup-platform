from django.urls import path

from .views import StartupMessageListAPIView, StartupMessageListCreateAPIView


urlpatterns = [
    path("startups/<uuid:startup_id>/messages/", StartupMessageListCreateAPIView.as_view(), name="startup-messages"),
]
