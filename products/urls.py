from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    SupplyListCreateView,
    SupplyDetailView,
)

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="product-list-create"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("supplies/", SupplyListCreateView.as_view(), name="supply-list-create"),
    path("supplies/<int:pk>/", SupplyDetailView.as_view(), name="supply-detail"),
]
