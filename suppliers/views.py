from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Supplier
from .serializers import SupplierSerializer, SupplierCreateUpdateSerializer
from .permissions import IsCompanyMember


def _get_user_company_id(request):
    user = request.user
    if user.is_authenticated and hasattr(user, "company_id"):
        return user.company_id
    return None


class SupplierListCreateView(generics.ListCreateAPIView):
    """
    GET: список поставщиков компании (владелец/сотрудник).
    POST: добавить поставщика (владелец/сотрудник).
    """
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        company_id = _get_user_company_id(self.request)
        if company_id:
            return Supplier.objects.filter(company_id=company_id).select_related("company")
        return Supplier.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupplierCreateUpdateSerializer
        return SupplierSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="Название поставщика"),
                "contact_info": openapi.Schema(type=openapi.TYPE_STRING, description="Контакты"),
            },
        ),
        responses={201: SupplierSerializer(), 403: "Нет доступа"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE поставщика. Доступно владельцу и сотрудникам.
    """
    permission_classes = (IsCompanyMember,)

    def get_queryset(self):
        company_id = _get_user_company_id(self.request)
        if company_id:
            return Supplier.objects.filter(company_id=company_id).select_related("company")
        return Supplier.objects.none()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return SupplierCreateUpdateSerializer
        return SupplierSerializer
