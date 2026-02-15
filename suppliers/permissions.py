from rest_framework import permissions


class IsCompanyMember(permissions.BasePermission):
    """
    Доступ к CRUD поставщиков: владелец и сотрудники компании.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.company_id

    def has_object_permission(self, request, view, obj):
        return request.user.company_id == obj.company_id
