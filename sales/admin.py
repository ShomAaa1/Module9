from django.contrib import admin
from .models import Sale, ProductSale


class ProductSaleInline(admin.TabularInline):
    model = ProductSale
    extra = 0
    raw_id_fields = ("product",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer_name", "company", "sale_date", "created_at")
    list_display_links = ("id", "buyer_name")
    list_filter = ("company", "sale_date")
    search_fields = ("buyer_name",)
    raw_id_fields = ("company",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (ProductSaleInline,)
