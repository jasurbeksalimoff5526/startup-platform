from django.urls import path

from .views import StartupMessageListAPIView


urlpatterns = [
    path("startups/<uuid:startup_id>/messages/", StartupMessageListAPIView.as_view(), name="startup-messages"),
]
