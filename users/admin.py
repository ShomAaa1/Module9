from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_company_owner", "company", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_company_owner")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    raw_id_fields = ("company",)

    # Добавляем новые поля в форму редактирования
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Компания", {"fields": ("company", "is_company_owner")}),
    )
