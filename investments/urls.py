from django.urls import path

from .views import StartupInvestmentListCreateAPIView


urlpatterns = [
    path(
        "startups/<uuid:startup_id>/investments/",
        StartupInvestmentListCreateAPIView.as_view(),
        name="startup-investments",
    ),
]
