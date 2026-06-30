from django.urls import path

from .views import StartupDonationListCreateAPIView


urlpatterns = [
    path(
        "startups/<uuid:startup_id>/donations/",
        StartupDonationListCreateAPIView.as_view(),
        name="startup-donations",
    ),
]
