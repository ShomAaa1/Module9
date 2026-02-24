from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from products.models import Product
from .models import Sale, ProductSale


# ─── Чтение ───


class ProductSaleReadSerializer(serializers.ModelSerializer):
    """Товар в продаже (чтение)."""
    product_id = serializers.IntegerField(source="product.id")
    product_title = serializers.CharField(source="product.title")

    class Meta:
        model = ProductSale
        fields = ("product_id", "product_title", "quantity")


class SaleSerializer(serializers.ModelSerializer):
    """Продажа (чтение)."""
    product_sales = ProductSaleReadSerializer(many=True, read_only=True)
    company_title = serializers.CharField(source="company.title", read_only=True)

    class Meta:
        model = Sale
        fields = (
            "id", "buyer_name", "company", "company_title",
            "product_sales", "sale_date",
            "created_at", "updated_at",
        )
        read_only_fields = fields


# ─── Создание ───


class ProductSaleItemSerializer(serializers.Serializer):
    """Элемент списка товаров в продаже (для запроса на создание)."""
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class SaleCreateSerializer(serializers.Serializer):
    """
    Создание продажи.
    Принимает: buyer_name, sale_date (опционально), product_sales [{product, quantity}].
    Уменьшает quantity товаров на складе.
    """
    buyer_name = serializers.CharField(max_length=255)
    sale_date = serializers.DateTimeField(required=False)
    product_sales = ProductSaleItemSerializer(many=True)

    def validate_sale_date(self, value):
        if value and value > timezone.now():
            raise serializers.ValidationError(
                "Дата продажи не может быть позже текущей даты."
            )
        return value

    def validate_product_sales(self, value):
        if not value:
            raise serializers.ValidationError("Список товаров не может быть пустым.")
        user = self.context["request"].user

        merged: dict[int, int] = {}
        for item in value:
            merged[item["product"]] = merged.get(item["product"], 0) + item["quantity"]

        product_ids = list(merged.keys())
        products = Product.objects.filter(id__in=product_ids).select_related("storage")
        found_ids = {p.id for p in products}
        missing = set(product_ids) - found_ids
        if missing:
            raise serializers.ValidationError(f"Товары не найдены: {missing}")
        for p in products:
            if p.storage.company_id != user.company_id:
                raise serializers.ValidationError(
                    f"Товар «{p.title}» не принадлежит вашей компании."
                )
            if p.quantity < merged[p.id]:
                raise serializers.ValidationError(
                    f"Недостаточно товара «{p.title}» на складе "
                    f"(доступно: {p.quantity}, запрошено: {merged[p.id]})."
                )

        return [{"product": pid, "quantity": qty} for pid, qty in merged.items()]

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        sale = Sale.objects.create(
            buyer_name=validated_data["buyer_name"],
            company_id=user.company_id,
            sale_date=validated_data.get("sale_date", timezone.now()),
        )
        product_ids = [item["product"] for item in validated_data["product_sales"]]
        products_map = {
            p.id: p
            for p in Product.objects.filter(id__in=product_ids).select_for_update()
        }

        sale_items = []
        for item in validated_data["product_sales"]:
            product = products_map[item["product"]]
            product.quantity -= item["quantity"]
            product.save(update_fields=["quantity"])
            sale_items.append(ProductSale(
                sale=sale,
                product=product,
                quantity=item["quantity"],
            ))
        ProductSale.objects.bulk_create(sale_items)
        return sale


# ─── Обновление ───


class SaleUpdateSerializer(serializers.ModelSerializer):
    """Обновление продажи: только buyer_name и sale_date."""
    class Meta:
        model = Sale
        fields = ("id", "buyer_name", "sale_date", "updated_at")
        read_only_fields = ("id", "updated_at")

    def validate_sale_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError(
                "Дата продажи не может быть позже текущей даты."
            )
        return value
