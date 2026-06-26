from django.urls import path

from .views import CategoryListCreateAPIView, StartupListCreateAPIView, StartupDetailAPIView


urlpatterns = [
    path("categories/", CategoryListCreateAPIView.as_view(), name="category-list-create"),
    path("", StartupListCreateAPIView.as_view(), name="startup-list-create"),
    path("<uuid:pk>/", StartupDetailAPIView.as_view(), name="startup-detail"),
]
