from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView, UpdateAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .profiles import InvestorProfile, MentorProfile
from .serializer import (
    ChangePasswordSerializer,
    InvestorProfileSerializer,
    LoginSerializer,
    MentorProfileSerializer,
    ProfileSerializer,
    RegisterSerializer,
)


class RegisterView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all()


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            return Response(
                {"message": "Login muvaffaqiyatli", "tokens": user.token()},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"message": "Refresh token xato"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logout muvaffaqiyatli"},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"message": "Refresh token xato"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProfileView(APIView):
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            instance=request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)

        return Response(
            {"message": "Parol muvaffaqiyatli o'zgartirildi."},
            status=status.HTTP_200_OK,
        )


class MentorProfileView(UpdateAPIView):
    serializer_class = MentorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = MentorProfile.objects.get_or_create(
            user=self.request.user,
            defaults={"expertise": "", "years_of_experience": 0},
        )
        return profile


class InvestorProfileView(UpdateAPIView):
    serializer_class = InvestorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = InvestorProfile.objects.get_or_create(user=self.request.user)
        return profile
