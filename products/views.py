from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Product, Supply, Sale
from .serializers import (
    ProductSerializer,
    ProductCreateUpdateSerializer,
    SupplySerializer,
    SupplyCreateSerializer,
    SaleSerializer,
    SaleCreateSerializer,
)
from .permissions import IsCompanyMember


def _get_user_company(request):
    """Безопасно получить company_id (None для анонимных пользователей)."""
    user = request.user
    if user.is_authenticated and hasattr(user, "company_id"):
        return user.company_id
    return None


# ─── Товары ───


class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET: товары на складах компании.
    POST: добавить товар (владелец/сотрудник).
    """
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        company_id = _get_user_company(self.request)
        if company_id:
            return Product.objects.filter(storage__company_id=company_id).select_related("storage")
        return Product.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductCreateUpdateSerializer
        return ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE товара."""
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        company_id = _get_user_company(self.request)
        if company_id:
            return Product.objects.filter(storage__company_id=company_id).select_related("storage")
        return Product.objects.none()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProductCreateUpdateSerializer
        return ProductSerializer


# ─── Поставки ───


class SupplyListCreateView(generics.ListCreateAPIView):
    """
    GET: список поставок компании.
    POST: создать новую поставку (увеличивает остаток товара).
    """
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        company_id = _get_user_company(self.request)
        if company_id:
            return Supply.objects.filter(
                product__storage__company_id=company_id
            ).select_related("product", "supplier", "created_by")
        return Supply.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupplyCreateSerializer
        return SupplySerializer


class SupplyDetailView(generics.RetrieveAPIView):
    """GET детали поставки."""
    permission_classes = (IsCompanyMember,)
    serializer_class = SupplySerializer

    def get_queryset(self):
        company_id = _get_user_company(self.request)
        if company_id:
            return Supply.objects.filter(
                product__storage__company_id=company_id
            ).select_related("product", "supplier", "created_by")
        return Supply.objects.none()


# ─── Продажи ───


class SaleListCreateView(generics.ListCreateAPIView):
    """
    GET: список продаж компании.
    POST: создать продажу (уменьшает остаток товара).
    """
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        company_id = _get_user_company(self.request)
        if company_id:
            return Sale.objects.filter(
                product__storage__company_id=company_id
            ).select_related("product", "created_by")
        return Sale.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SaleCreateSerializer
        return SaleSerializer


class SaleDetailView(generics.RetrieveUpdateAPIView):
    """
    GET: детали продажи.
    PUT/PATCH: редактирование продажи (владелец/сотрудник).
    """
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        company_id = _get_user_company(self.request)
        if company_id:
            return Sale.objects.filter(
                product__storage__company_id=company_id
            ).select_related("product", "created_by")
        return Sale.objects.none()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return SaleCreateSerializer
        return SaleSerializer
