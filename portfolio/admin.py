from django.contrib import admin
from django.utils.html import format_html

from .models import ContactMessage, Project, SocialLink


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("display_name", "platform", "url", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("platform", "is_active")
    ordering = ("order", "id")
    fields = ("platform", "label", "url", "order", "is_active")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title_uz", "tier", "status", "order", "is_active", "has_cover")
    list_editable = ("tier", "status", "order", "is_active")
    list_filter = ("tier", "status", "is_active")
    search_fields = ("title_uz", "title_ru", "title_en", "tags")
    prepopulated_fields = {"slug": ("title_en",)}
    readonly_fields = ("cover_preview",)
    fieldsets = (
        ("Ko'rinish", {"fields": ("slug", "tier", "status", "order", "is_active")}),
        ("O'zbekcha", {"fields": ("title_uz", "desc_uz", "highlights_uz")}),
        ("Русский", {"fields": ("title_ru", "desc_ru", "highlights_ru")}),
        ("English", {"fields": ("title_en", "desc_en", "highlights_en")}),
        ("Havolalar va texnologiyalar", {"fields": ("link", "github", "tags")}),
        ("Muqova", {"fields": ("cover", "cover_preview")}),
    )

    @admin.display(boolean=True, description="Muqova")
    def has_cover(self, obj):
        return bool(obj.cover)

    @admin.display(description="Ko'rinishi")
    def cover_preview(self, obj):
        if not obj.cover:
            return "—"
        return format_html('<img src="{}" style="max-width:420px;border-radius:8px">', obj.cover.url)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "contact", "short_message", "lang", "created_at", "is_read", "telegram_sent")
    list_filter = ("is_read", "lang", "telegram_sent")
    search_fields = ("name", "contact", "message")
    readonly_fields = ("name", "contact", "message", "lang", "created_at", "telegram_sent")
    fields = ("name", "contact", "message", "lang", "created_at", "telegram_sent", "is_read")
    actions = ("mark_read",)

    def has_add_permission(self, request):
        return False

    @admin.display(description="Xabar")
    def short_message(self, obj):
        return obj.message if len(obj.message) <= 60 else obj.message[:60] + "…"

    @admin.action(description="O'qilgan deb belgilash")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
