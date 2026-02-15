"""
URL configuration for CRM project.
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="CRM API",
        default_version="v1",
        description="API CRM с JWT-аутентификацией. Компании и склады.",
        terms_of_service="",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", RedirectView.as_view(url="/swagger/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/v1/", include("core.api_urls")),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
