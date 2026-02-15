from rest_framework import permissions


class IsCompanyMember(permissions.BasePermission):
    """Доступ к товарам/поставкам/продажам: владелец и сотрудники компании."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.company_id
