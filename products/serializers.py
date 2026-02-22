from django.db import transaction
from rest_framework import serializers
from .models import Product, Supply, SupplyProduct


# ─── Product ───


class ProductSerializer(serializers.ModelSerializer):
    """Товар (чтение)."""
    storage_address = serializers.CharField(source="storage.address", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "title", "purchase_price", "sale_price",
            "quantity", "storage", "storage_address",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "quantity", "created_at", "updated_at")


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление товара. quantity всегда 0 при создании (пополнение только через поставки)."""
    class Meta:
        model = Product
        fields = ("id", "title", "purchase_price", "sale_price", "storage", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_storage(self, value):
        user = self.context["request"].user
        if value.company_id != user.company_id:
            raise serializers.ValidationError("Склад не принадлежит вашей компании.")
        return value

    def create(self, validated_data):
        validated_data["quantity"] = 0
        return super().create(validated_data)


# ─── Supply ───


class SupplyProductItemSerializer(serializers.Serializer):
    """Элемент списка товаров в поставке (для запроса)."""
    id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class SupplyCreateSerializer(serializers.Serializer):
    """
    Создание поставки.
    Принимает: supplier_id + products [{id, quantity}, ...].
    Увеличивает quantity товаров.
    """
    supplier_id = serializers.IntegerField()
    products = SupplyProductItemSerializer(many=True)

    def validate_supplier_id(self, value):
        from suppliers.models import Supplier
        user = self.context["request"].user
        try:
            supplier = Supplier.objects.get(id=value)
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Поставщик не найден.")
        if supplier.company_id != user.company_id:
            raise serializers.ValidationError("Поставщик не принадлежит вашей компании.")
        return value

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError("Список товаров не может быть пустым.")
        user = self.context["request"].user

        merged: dict[int, int] = {}
        for item in value:
            if item["quantity"] <= 0:
                raise serializers.ValidationError("Количество должно быть положительным.")
            merged[item["id"]] = merged.get(item["id"], 0) + item["quantity"]

        product_ids = list(merged.keys())
        products = Product.objects.filter(id__in=product_ids).select_related("storage")
        found_ids = {p.id for p in products}
        missing = set(product_ids) - found_ids
        if missing:
            raise serializers.ValidationError(f"Товары не найдены: {missing}")
        for p in products:
            if p.storage.company_id != user.company_id:
                raise serializers.ValidationError(f"Товар «{p.title}» не принадлежит вашей компании.")

        return [{"id": pid, "quantity": qty} for pid, qty in merged.items()]

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        supply = Supply.objects.create(
            supplier_id=validated_data["supplier_id"],
            created_by=user,
        )
        product_ids = [item["id"] for item in validated_data["products"]]
        products_map = {p.id: p for p in Product.objects.filter(id__in=product_ids).select_for_update()}

        supply_products = []
        for item in validated_data["products"]:
            product = products_map[item["id"]]
            product.quantity += item["quantity"]
            product.save(update_fields=["quantity"])
            supply_products.append(SupplyProduct(
                supply=supply,
                product=product,
                quantity=item["quantity"],
            ))
        SupplyProduct.objects.bulk_create(supply_products)
        return supply


class SupplyProductReadSerializer(serializers.ModelSerializer):
    """Элемент поставки (для чтения)."""
    product_id = serializers.IntegerField(source="product.id")
    product_title = serializers.CharField(source="product.title")

    class Meta:
        model = SupplyProduct
        fields = ("product_id", "product_title", "quantity")


class SupplySerializer(serializers.ModelSerializer):
    """Поставка (чтение)."""
    supplier_title = serializers.CharField(source="supplier.title", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True, default=None)
    items = SupplyProductReadSerializer(many=True, read_only=True)

    class Meta:
        model = Supply
        fields = (
            "id", "supplier", "supplier_title",
            "items", "delivery_date",
            "created_by", "created_by_username",
        )
        read_only_fields = fields
