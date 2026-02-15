from rest_framework import permissions
from companies.permissions import is_company_owner


class IsCompanyOwnerForStorage(permissions.BasePermission):
    """
    Создание/редактирование/удаление склада: только владелец компании.
    Получение информации: все пользователи, связанные с компанией.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Чтение: любой сотрудник компании
            return request.user.company_id == obj.company_id
        # Запись: только владелец
        return is_company_owner(request.user, obj.company)
