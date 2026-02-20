from rest_framework import generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Product, Supply
from .serializers import (
    ProductSerializer,
    ProductCreateUpdateSerializer,
    SupplySerializer,
    SupplyCreateSerializer,
)
from .permissions import IsCompanyMember


def _get_company_id(request):
    user = request.user
    if user.is_authenticated and getattr(user, "company_id", None):
        return user.company_id
    return None


# ─── Товары ───


class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET: список товаров компании.
    POST: создать товар (quantity=0, пополнение только через поставки).
    """
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        cid = _get_company_id(self.request)
        if cid:
            return Product.objects.filter(storage__company_id=cid).select_related("storage")
        return Product.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductCreateUpdateSerializer
        return ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE товара."""
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        cid = _get_company_id(self.request)
        if cid:
            return Product.objects.filter(storage__company_id=cid).select_related("storage")
        return Product.objects.none()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProductCreateUpdateSerializer
        return ProductSerializer


# ─── Поставки ───


class SupplyListCreateView(generics.GenericAPIView):
    """
    GET: список поставок компании.
    POST: создать поставку (supplier_id + products [{id, quantity}]).
    """
    permission_classes = (IsCompanyMember,)
    queryset = Supply.objects.none()

    def get_queryset(self):
        cid = _get_company_id(self.request)
        if cid:
            return Supply.objects.filter(
                supplier__company_id=cid
            ).select_related("supplier", "created_by").prefetch_related("items__product")
        return Supply.objects.none()

    @swagger_auto_schema(responses={200: SupplySerializer(many=True)})
    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = SupplySerializer(qs, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["supplier_id", "products"],
            properties={
                "supplier_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID поставщика"),
                "products": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        required=["id", "quantity"],
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара"),
                            "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, description="Количество (>0)"),
                        },
                    ),
                ),
            },
        ),
        responses={201: SupplySerializer(), 400: "Ошибка валидации"},
    )
    def post(self, request, *args, **kwargs):
        serializer = SupplyCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        supply = serializer.save()
        return Response(
            SupplySerializer(supply).data,
            status=status.HTTP_201_CREATED,
        )


class SupplyDetailView(generics.RetrieveAPIView):
    """GET детали поставки."""
    permission_classes = (IsCompanyMember,)
    serializer_class = SupplySerializer

    def get_queryset(self):
        cid = _get_company_id(self.request)
        if cid:
            return Supply.objects.filter(
                supplier__company_id=cid
            ).select_related("supplier", "created_by").prefetch_related("items__product")
        return Supply.objects.none()
