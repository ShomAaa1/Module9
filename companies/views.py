from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Company
from .serializers import CompanySerializer, CompanyCreateUpdateSerializer
from .permissions import IsCompanyOwnerOrReadOnly


class CompanyListCreateView(generics.ListCreateAPIView):
    """
    GET: список компаний (все авторизованные).
    POST: создание компании (текущий пользователь становится владельцем).
    """
    permission_classes = (IsCompanyOwnerOrReadOnly,)
    queryset = Company.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CompanyCreateUpdateSerializer
        return CompanySerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["inn", "title"],
            properties={
                "inn": openapi.Schema(type=openapi.TYPE_STRING, description="ИНН (уникальный)"),
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="Название компании"),
            },
        ),
        responses={201: CompanySerializer(), 400: "Ошибка валидации"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: информация о компании (все авторизованные).
    PUT/PATCH/DELETE: только владелец компании.
    """
    permission_classes = (IsCompanyOwnerOrReadOnly,)
    queryset = Company.objects.all()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return CompanyCreateUpdateSerializer
        return CompanySerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "inn": openapi.Schema(type=openapi.TYPE_STRING),
                "title": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: CompanySerializer(), 403: "Только владелец", 404: "Не найдена"},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "inn": openapi.Schema(type=openapi.TYPE_STRING),
                "title": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: CompanySerializer(), 403: "Только владелец", 404: "Не найдена"},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
