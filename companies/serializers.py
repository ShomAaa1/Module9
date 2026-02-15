from rest_framework import serializers
from .models import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanyOwnerSerializer(serializers.ModelSerializer):
    """Краткий сериализатор владельца."""
    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = fields


class CompanySerializer(serializers.ModelSerializer):
    """Чтение компании. Показывает владельца и кол-во сотрудников."""
    owner = serializers.SerializerMethodField()
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ("id", "inn", "title", "owner", "employees_count", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def get_owner(self, obj):
        owner = obj.get_owner()
        if owner:
            return CompanyOwnerSerializer(owner).data
        return None

    def get_employees_count(self, obj):
        return obj.employees.count()


class CompanyCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание компании: текущий пользователь становится владельцем."""
    class Meta:
        model = Company
        fields = ("id", "inn", "title", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        user = self.context["request"].user
        if user.is_company_owner and user.company_id is not None:
            raise serializers.ValidationError("Вы уже являетесь владельцем компании.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        company = super().create(validated_data)
        user.company = company
        user.is_company_owner = True
        user.save(update_fields=["company", "is_company_owner"])
        return company
