from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ChangePasswordView,
    InvestorProfileView,
    LoginView,
    LogoutView,
    MentorProfileView,
    ProfileView,
    RegisterView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("profile/", ProfileView.as_view(), name="auth-profile"),
    path("change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
    path("mentor-profile/", MentorProfileView.as_view(), name="auth-mentor-profile"),
    path("investor-profile/", InvestorProfileView.as_view(), name="auth-investor-profile"),
]
