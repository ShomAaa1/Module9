"""
API v1 URL routing. Imported after apps are ready to avoid circular imports.
"""
from django.urls import path, include

urlpatterns = [
    path("auth/", include("users.urls")),
    path("companies/", include("companies.urls")),
    path("storages/", include("storages.urls")),
    path("suppliers/", include("suppliers.urls")),
    path("products/", include("products.urls")),
]
