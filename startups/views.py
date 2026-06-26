from django.db.models import F
from django.db.models import Q
from rest_framework import filters
from rest_framework.generics import (
    ListCreateAPIView as CategoryListCreateAPIViewBase,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from shared.permissions import IsFounderOrReadOnly, IsOwnerOrAdmin
from .models import Category, Startup
from .serializer import CategorySerializer, StartupSerializer


class StartupPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class CategoryListCreateAPIView(CategoryListCreateAPIViewBase):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsFounderOrReadOnly]


class StartupListCreateAPIView(ListCreateAPIView):
    serializer_class = StartupSerializer
    permission_classes = [IsFounderOrReadOnly]
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
        serializer.save(owner=self.request.user)


class StartupDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = StartupSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_authenticated", False):
            if getattr(user, "is_admin", False):
                return Startup.objects.all()
            return Startup.objects.filter(Q(is_public=True) | Q(owner=user))
        return Startup.objects.filter(is_public=True)

    def retrieve(self, request, *args, **kwargs):
        startup = self.get_object()
        Startup.objects.filter(pk=startup.pk).update(views=F("views") + 1)
        startup.refresh_from_db()
        serializer = self.get_serializer(startup)
        return Response(serializer.data)
