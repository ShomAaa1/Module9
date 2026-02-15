from django.contrib import admin
from .models import Storage


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "address", "created_at", "updated_at")
    list_display_links = ("id", "address")
    list_filter = ("created_at",)
    search_fields = ("address", "company__title", "company__inn")
    raw_id_fields = ("company",)
    readonly_fields = ("created_at", "updated_at")
