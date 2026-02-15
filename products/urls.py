from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    SupplyListCreateView,
    SupplyDetailView,
    SaleListCreateView,
    SaleDetailView,
)

urlpatterns = [
    # Товары
    path("", ProductListCreateView.as_view(), name="product-list-create"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    # Поставки
    path("supplies/", SupplyListCreateView.as_view(), name="supply-list-create"),
    path("supplies/<int:pk>/", SupplyDetailView.as_view(), name="supply-detail"),
    # Продажи
    path("sales/", SaleListCreateView.as_view(), name="sale-list-create"),
    path("sales/<int:pk>/", SaleDetailView.as_view(), name="sale-detail"),
]
