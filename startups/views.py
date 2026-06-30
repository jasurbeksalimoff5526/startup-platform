from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    ListCreateAPIView as CategoryListCreateAPIViewBase,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import IsAdmin, IsOwnerOrAdmin, IsAdminOrReadOnly
from .models import (
    Application,
    Bookmark,
    Category,
    Startup,
    StartupMember,
    Vacancy,
    FOUNDER,
)
from .permissions import IsFounder, IsVacancyOwnerOrAdmin, IsApplicationOwner
from .serializer import (
    ApplicationSerializer,
    BookmarkSerializer,
    CategorySerializer,
    StartupSerializer,
    VacancySerializer,
)


class StartupPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class CategoryListCreateAPIView(CategoryListCreateAPIViewBase):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class StartupListCreateAPIView(ListCreateAPIView):
    serializer_class = StartupSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StartupPagination
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "title",
        "short_description",
        "description",
    ]

    def get_queryset(self):
        queryset = Startup.objects.filter(is_public=True)
        category = self.request.query_params.get("category")
        stage = self.request.query_params.get("stage")
        search = self.request.query_params.get("q")

        if category:
            queryset = queryset.filter(category_id=category)
        if stage:
            queryset = queryset.filter(stage=stage)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(short_description__icontains=search)
                | Q(description__icontains=search)
            )

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        startup = serializer.save(owner=self.request.user)
        StartupMember.objects.get_or_create(
            startup=startup,
            user=self.request.user,
            defaults={"role": FOUNDER},
        )


class StartupDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = StartupSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_authenticated", False):
            if getattr(user, "is_staff", False):
                return Startup.objects.all()
            return Startup.objects.filter(Q(is_public=True) | Q(owner=user))
        return Startup.objects.filter(is_public=True)

    def retrieve(self, request, *args, **kwargs):
        startup = self.get_object()
        Startup.objects.filter(pk=startup.pk).update(views=F("views") + 1)
        startup.refresh_from_db()
        serializer = self.get_serializer(startup)
        return Response(serializer.data)


class BookmarkListCreateAPIView(ListCreateAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StartupPagination

    def get_queryset(self):
        return (
            Bookmark.objects.filter(user=self.request.user)
            .select_related("startup")
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        startup = serializer.validated_data["startup"]
        bookmark, _ = Bookmark.objects.get_or_create(
            user=request.user, startup=startup
        )
        output = self.get_serializer(bookmark)
        return Response(output.data, status=status.HTTP_201_CREATED)


class BookmarkDestroyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, startup_id):
        deleted, _ = Bookmark.objects.filter(
            user=request.user, startup_id=startup_id
        ).delete()
        if deleted == 0:
            return Response(
                {"detail": "Bookmark topilmadi."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class VacancyListCreateAPIView(ListCreateAPIView):
    serializer_class = VacancySerializer
    permission_classes = [IsFounder]
    pagination_class = StartupPagination

    def get_queryset(self):
        startup = get_object_or_404(Startup, pk=self.kwargs["startup_id"])
        return Vacancy.objects.filter(startup=startup).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        startup = get_object_or_404(Startup, pk=self.kwargs["startup_id"])
        is_founder = StartupMember.objects.filter(
            startup=startup, user=request.user, role=FOUNDER
        ).exists()
        if not is_founder and not request.user.is_staff:
            raise PermissionDenied("Faqat Founder vakansiya ochishi mumkin.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vacancy = serializer.save(startup=startup)
        output = self.get_serializer(vacancy)
        return Response(output.data, status=status.HTTP_201_CREATED)


class VacancyDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = VacancySerializer
    permission_classes = [permissions.IsAuthenticated, IsVacancyOwnerOrAdmin]
    queryset = Vacancy.objects.all()


class _ApplicationCreateInputSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_blank=True, default="")


class ApplicationListCreateAPIView(ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StartupPagination

    def get_queryset(self):
        vacancy = get_object_or_404(Vacancy, pk=self.kwargs["vacancy_id"])
        user = self.request.user
        qs = Application.objects.filter(vacancy=vacancy).select_related(
            "applicant", "vacancy"
        )
        if StartupMember.objects.filter(
            startup=vacancy.startup, user=user, role=FOUNDER
        ).exists() or user.is_staff:
            return qs
        return qs.filter(applicant=user)

    def create(self, request, *args, **kwargs):
        vacancy = get_object_or_404(Vacancy, pk=self.kwargs["vacancy_id"])
        if vacancy.status != Vacancy.OPEN:
            raise PermissionDenied("Bu vakansiya yopiq.")
        input_serializer = _ApplicationCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            application, created = Application.objects.get_or_create(
                vacancy=vacancy,
                applicant=request.user,
                defaults={
                    "message": input_serializer.validated_data.get("message", "")
                },
            )
        output = self.get_serializer(application)
        return Response(
            output.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class ApplicationDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsApplicationOwner]
    queryset = Application.objects.all()

    def perform_update(self, serializer):
        new_status = self.request.data.get("status")
        instance = serializer.instance
        if new_status == Application.ACCEPTED and instance.status != Application.ACCEPTED:
            with transaction.atomic():
                serializer.save(status=Application.ACCEPTED)
                StartupMember.objects.get_or_create(
                    startup=instance.vacancy.startup,
                    user=instance.applicant,
                    defaults={"role": instance.vacancy.role},
                )
        elif new_status in (
            Application.PENDING,
            Application.ACCEPTED,
            Application.REJECTED,
        ):
            serializer.save(status=new_status)
        else:
            serializer.save()
