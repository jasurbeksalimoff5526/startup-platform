from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import ChangePasswordView, LoginView, LogoutView, ProfileView, RegisterView


urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("logout", LogoutView.as_view()),
    path("refresh", TokenRefreshView.as_view()),
    path("profile", ProfileView.as_view()),
    path("change-password", ChangePasswordView.as_view()),
]
