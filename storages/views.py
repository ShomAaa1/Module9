from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Storage
from .serializers import StorageSerializer, StorageCreateUpdateSerializer
from .permissions import IsCompanyOwnerForStorage


class StorageListCreateView(generics.ListCreateAPIView):
    """
    GET: список складов компании текущего пользователя.
    POST: создание склада (только владелец компании).
    """
    permission_classes = (IsCompanyOwnerForStorage,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, "company_id", None):
            return Storage.objects.filter(company_id=user.company_id).select_related("company")
        return Storage.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StorageCreateUpdateSerializer
        return StorageSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["address"],
            properties={
                "address": openapi.Schema(type=openapi.TYPE_STRING, description="Адрес склада"),
            },
        ),
        responses={201: StorageSerializer(), 403: "Только владелец компании"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class StorageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: информация о складе (сотрудники компании).
    PUT/PATCH/DELETE: только владелец компании.
    """
    permission_classes = (IsCompanyOwnerForStorage,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, "company_id", None):
            return Storage.objects.filter(company_id=user.company_id).select_related("company")
        return Storage.objects.none()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return StorageCreateUpdateSerializer
        return StorageSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"address": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={200: StorageSerializer(), 403: "Нет доступа", 404: "Склад не найден"},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"address": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={200: StorageSerializer(), 403: "Нет доступа", 404: "Склад не найден"},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
