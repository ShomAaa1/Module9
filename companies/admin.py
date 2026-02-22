from django.contrib import admin
from .models import Company, JoinRequest


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "inn", "title", "get_owner", "created_at", "updated_at")
    list_display_links = ("id", "title")
    list_filter = ("created_at",)
    search_fields = ("inn", "title")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Владелец")
    def get_owner(self, obj):
        owner = obj.get_owner()
        return owner.username if owner else "—"


@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "company", "status", "created_at", "reviewed_at")
    list_display_links = ("id", "user")
    list_filter = ("status", "company")
    search_fields = ("user__username", "user__email", "company__title")
    raw_id_fields = ("user", "company")
    readonly_fields = ("created_at",)
