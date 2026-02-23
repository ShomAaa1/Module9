from rest_framework import generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Sale
from .serializers import SaleSerializer, SaleCreateSerializer, SaleUpdateSerializer
from .permissions import IsCompanyMember


class SaleListCreateView(generics.ListCreateAPIView):
    """
    GET: список продаж компании. Поддерживает фильтрацию по периоду:
         ?date_from=2025-01-01&date_to=2025-12-31
    POST: создать продажу (buyer_name + product_sales [{product, quantity}]).
    """
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        user = self.request.user
        if not user.company_id:
            return Sale.objects.none()
        qs = Sale.objects.filter(
            company_id=user.company_id,
        ).select_related("company").prefetch_related("product_sales__product")

        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(sale_date__gte=date_from)
        if date_to:
            qs = qs.filter(sale_date__lte=date_to)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SaleCreateSerializer
        return SaleSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "date_from", openapi.IN_QUERY,
                description="Начало периода (YYYY-MM-DD)",
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "date_to", openapi.IN_QUERY,
                description="Конец периода (YYYY-MM-DD)",
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
            ),
        ],
        responses={200: SaleSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["buyer_name", "product_sales"],
            properties={
                "buyer_name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Имя покупателя",
                ),
                "sale_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                    description="Дата продажи (по умолчанию — текущая)",
                ),
                "product_sales": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        required=["product", "quantity"],
                        properties={
                            "product": openapi.Schema(
                                type=openapi.TYPE_INTEGER, description="ID товара",
                            ),
                            "quantity": openapi.Schema(
                                type=openapi.TYPE_INTEGER, description="Количество (>0)",
                            ),
                        },
                    ),
                ),
            },
        ),
        responses={201: SaleSerializer(), 400: "Ошибка валидации"},
    )
    def post(self, request, *args, **kwargs):
        serializer = SaleCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        sale = serializer.save()
        return Response(
            SaleSerializer(sale).data,
            status=status.HTTP_201_CREATED,
        )


class SaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: детали продажи.
    PUT/PATCH: изменить только buyer_name и sale_date.
    DELETE: удалить продажу (товары возвращаются на склад).
    """
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        user = self.request.user
        if not user.company_id:
            return Sale.objects.none()
        return Sale.objects.filter(
            company_id=user.company_id,
        ).select_related("company").prefetch_related("product_sales__product")

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return SaleUpdateSerializer
        return SaleSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "buyer_name": openapi.Schema(type=openapi.TYPE_STRING),
                "sale_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                ),
            },
        ),
        responses={200: SaleSerializer(), 403: "Нет доступа", 404: "Не найдена"},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "buyer_name": openapi.Schema(type=openapi.TYPE_STRING),
                "sale_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                ),
            },
        ),
        responses={200: SaleSerializer(), 403: "Нет доступа", 404: "Не найдена"},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={204: "Продажа удалена, товары возвращены на склад"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
