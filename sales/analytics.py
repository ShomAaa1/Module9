from datetime import timedelta

from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ProductSale
from .permissions import IsCompanyMember

PERIOD_PARAM = openapi.Parameter(
    "period", openapi.IN_QUERY,
    description="Пресет периода: day, week, month (игнорируется, если указаны date_from/date_to)",
    type=openapi.TYPE_STRING, enum=["day", "week", "month"],
)
DATE_FROM_PARAM = openapi.Parameter(
    "date_from", openapi.IN_QUERY,
    description="Начало периода (YYYY-MM-DD)",
    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
)
DATE_TO_PARAM = openapi.Parameter(
    "date_to", openapi.IN_QUERY,
    description="Конец периода (YYYY-MM-DD)",
    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
)
LIMIT_PARAM = openapi.Parameter(
    "limit", openapi.IN_QUERY,
    description="Количество записей в топе (по умолчанию 10)",
    type=openapi.TYPE_INTEGER,
)

PERIOD_DELTAS = {
    "day": timedelta(days=1),
    "week": timedelta(weeks=1),
    "month": timedelta(days=30),
}


def _get_date_range(request):
    """Извлекает диапазон дат из query-параметров или пресета period."""
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")
    if date_from or date_to:
        return date_from, date_to

    period = request.query_params.get("period")
    delta = PERIOD_DELTAS.get(period)
    if delta:
        now = timezone.now()
        return (now - delta).isoformat(), now.isoformat()
    return None, None


def _base_qs(request):
    """Базовый queryset ProductSale для компании пользователя с фильтрацией по датам."""
    qs = ProductSale.objects.filter(
        sale__company_id=request.user.company_id,
    )
    date_from, date_to = _get_date_range(request)
    if date_from:
        qs = qs.filter(sale__sale_date__gte=date_from)
    if date_to:
        qs = qs.filter(sale__sale_date__lte=date_to)
    return qs


REVENUE_EXPR = ExpressionWrapper(
    F("quantity") * F("product__sale_price"),
    output_field=DecimalField(max_digits=14, decimal_places=2),
)
COST_EXPR = ExpressionWrapper(
    F("quantity") * F("product__purchase_price"),
    output_field=DecimalField(max_digits=14, decimal_places=2),
)


class ProfitAnalyticsView(APIView):
    """Чистая и общая прибыль за выбранный период."""
    permission_classes = (IsCompanyMember,)

    @swagger_auto_schema(
        manual_parameters=[DATE_FROM_PARAM, DATE_TO_PARAM, PERIOD_PARAM],
        responses={200: openapi.Response(
            description="Прибыль",
            examples={"application/json": {
                "total_revenue": "15000.00",
                "total_cost": "9000.00",
                "net_profit": "6000.00",
                "sales_count": 12,
            }},
        )},
    )
    def get(self, request):
        qs = _base_qs(request)
        agg = qs.aggregate(
            total_revenue=Sum(REVENUE_EXPR),
            total_cost=Sum(COST_EXPR),
        )
        revenue = agg["total_revenue"] or 0
        cost = agg["total_cost"] or 0
        sales_count = qs.values("sale").distinct().count()

        return Response({
            "total_revenue": revenue,
            "total_cost": cost,
            "net_profit": revenue - cost,
            "sales_count": sales_count,
        })


class ProductsSoldAnalyticsView(APIView):
    """Количество проданных товаров: общее и по каждому товару."""
    permission_classes = (IsCompanyMember,)

    @swagger_auto_schema(
        manual_parameters=[DATE_FROM_PARAM, DATE_TO_PARAM, PERIOD_PARAM],
        responses={200: openapi.Response(
            description="Проданные товары",
            examples={"application/json": {
                "total_quantity": 150,
                "products": [
                    {"product_id": 1, "product_title": "Товар 1", "total_quantity": 80},
                    {"product_id": 2, "product_title": "Товар 2", "total_quantity": 70},
                ],
            }},
        )},
    )
    def get(self, request):
        qs = _base_qs(request)
        total = qs.aggregate(total=Sum("quantity"))["total"] or 0
        per_product = (
            qs.values(
                product_id=F("product__id"),
                product_title=F("product__title"),
            )
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")
        )
        return Response({
            "total_quantity": total,
            "products": list(per_product),
        })


class ProfitByProductAnalyticsView(APIView):
    """Товар с наибольшей и наименьшей чистой прибылью за период."""
    permission_classes = (IsCompanyMember,)

    @swagger_auto_schema(
        manual_parameters=[DATE_FROM_PARAM, DATE_TO_PARAM, PERIOD_PARAM],
        responses={200: openapi.Response(
            description="Прибыль по товарам",
            examples={"application/json": {
                "most_profitable": {
                    "product_id": 1, "product_title": "Товар 1",
                    "revenue": "10000.00", "cost": "5000.00", "net_profit": "5000.00",
                },
                "least_profitable": {
                    "product_id": 3, "product_title": "Товар 3",
                    "revenue": "500.00", "cost": "400.00", "net_profit": "100.00",
                },
            }},
        )},
    )
    def get(self, request):
        qs = _base_qs(request)
        per_product = (
            qs.values(
                product_id=F("product__id"),
                product_title=F("product__title"),
            )
            .annotate(
                revenue=Sum(REVENUE_EXPR),
                cost=Sum(COST_EXPR),
            )
            .annotate(
                net_profit=ExpressionWrapper(
                    F("revenue") - F("cost"),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                ),
            )
        )
        most = per_product.order_by("-net_profit").first()
        least = per_product.order_by("net_profit").first()

        return Response({
            "most_profitable": most,
            "least_profitable": least,
        })


class TopProductsAnalyticsView(APIView):
    """Топ самых продаваемых товаров за день / неделю / месяц / выбранный период."""
    permission_classes = (IsCompanyMember,)

    @swagger_auto_schema(
        manual_parameters=[DATE_FROM_PARAM, DATE_TO_PARAM, PERIOD_PARAM, LIMIT_PARAM],
        responses={200: openapi.Response(
            description="Топ товаров",
            examples={"application/json": {
                "period": "week",
                "top": [
                    {"product_id": 1, "product_title": "Товар 1", "total_quantity": 80},
                    {"product_id": 5, "product_title": "Товар 5", "total_quantity": 45},
                ],
            }},
        )},
    )
    def get(self, request):
        qs = _base_qs(request)
        limit = min(int(request.query_params.get("limit", 10)), 100)
        period = request.query_params.get("period")

        top = (
            qs.values(
                product_id=F("product__id"),
                product_title=F("product__title"),
            )
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")[:limit]
        )
        return Response({
            "period": period or "custom",
            "top": list(top),
        })
