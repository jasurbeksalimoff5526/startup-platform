from django.urls import path

from .views import (
    ApplicationDetailAPIView,
    ApplicationListCreateAPIView,
    BookmarkDestroyAPIView,
    BookmarkListCreateAPIView,
    CategoryListCreateAPIView,
    StartupDetailAPIView,
    StartupListCreateAPIView,
    VacancyDetailAPIView,
    VacancyListCreateAPIView,
)


urlpatterns = [
    path("categories/", CategoryListCreateAPIView.as_view(), name="category-list-create"),
    path("", StartupListCreateAPIView.as_view(), name="startup-list-create"),
    path("<uuid:pk>/", StartupDetailAPIView.as_view(), name="startup-detail"),
    path("bookmarks/", BookmarkListCreateAPIView.as_view(), name="bookmark-list-create"),
    path(
        "bookmarks/<uuid:startup_id>/",
        BookmarkDestroyAPIView.as_view(),
        name="bookmark-destroy",
    ),
    path(
        "<uuid:startup_id>/vacancies/",
        VacancyListCreateAPIView.as_view(),
        name="vacancy-list-create",
    ),
    path(
        "vacancies/<uuid:pk>/",
        VacancyDetailAPIView.as_view(),
        name="vacancy-detail",
    ),
    path(
        "vacancies/<uuid:vacancy_id>/applications/",
        ApplicationListCreateAPIView.as_view(),
        name="application-list-create",
    ),
    path(
        "applications/<uuid:pk>/",
        ApplicationDetailAPIView.as_view(),
        name="application-detail",
    ),
]
