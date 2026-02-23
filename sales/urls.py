from django.urls import path
from .views import SaleListCreateView, SaleDetailView
from .analytics import (
    ProfitAnalyticsView,
    ProductsSoldAnalyticsView,
    ProfitByProductAnalyticsView,
    TopProductsAnalyticsView,
)

urlpatterns = [
    path("", SaleListCreateView.as_view(), name="sale-list-create"),
    path("<int:pk>/", SaleDetailView.as_view(), name="sale-detail"),
    # Аналитика
    path("analytics/profit/", ProfitAnalyticsView.as_view(), name="analytics-profit"),
    path("analytics/products-sold/", ProductsSoldAnalyticsView.as_view(), name="analytics-products-sold"),
    path("analytics/profit-by-product/", ProfitByProductAnalyticsView.as_view(), name="analytics-profit-by-product"),
    path("analytics/top-products/", TopProductsAnalyticsView.as_view(), name="analytics-top-products"),
]
