from rest_framework import serializers
from .models import Storage


class StorageSerializer(serializers.ModelSerializer):
    """Склад (чтение). Компания — id + title."""
    company_title = serializers.CharField(source="company.title", read_only=True)

    class Meta:
        model = Storage
        fields = ("id", "address", "company", "company_title", "created_at", "updated_at")
        read_only_fields = ("id", "company", "company_title", "created_at", "updated_at")


class StorageCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление склада. company берётся из user.company (OneToOne)."""
    class Meta:
        model = Storage
        fields = ("id", "address", "company", "created_at", "updated_at")
        read_only_fields = ("id", "company", "created_at", "updated_at")

    def create(self, validated_data):
        user = self.context["request"].user
        if not user.is_company_owner or not user.company_id:
            raise serializers.ValidationError("Вы должны быть владельцем компании.")
        validated_data["company"] = user.company
        return super().create(validated_data)
