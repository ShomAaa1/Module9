from rest_framework import permissions


def is_company_owner(user, company):
    """Проверяет, является ли user владельцем company."""
    return (
        user.is_company_owner
        and user.company_id is not None
        and user.company_id == company.id
    )


class IsCompanyOwnerOrReadOnly(permissions.BasePermission):
    """
    Создание: любой авторизованный пользователь.
    Редактирование/удаление: только владелец компании (user.is_company_owner + user.company == obj).
    Чтение: любой авторизованный пользователь.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_company_owner(request.user, obj)
