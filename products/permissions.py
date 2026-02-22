from rest_framework import permissions


class IsCompanyMember(permissions.BasePermission):
    """Доступ к товарам/поставкам/продажам: владелец и сотрудники компании."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.company_id

    def has_object_permission(self, request, view, obj):
        cid = request.user.company_id
        if hasattr(obj, "storage"):
            return cid == obj.storage.company_id
        if hasattr(obj, "supplier"):
            return cid == obj.supplier.company_id
        return False
