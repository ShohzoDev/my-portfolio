from django.contrib import admin
from django.utils.html import format_html

from .models import ContactMessage, Project, SiteProfile, SocialLink


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("display_name", "platform", "url", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("platform", "is_active")
    ordering = ("order", "id")
    fields = ("platform", "label", "url", "order", "is_active")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title_uz", "site", "status", "is_founder", "order", "is_active")
    list_editable = ("status", "order", "is_active")
    list_filter = ("status", "is_active")
    search_fields = ("title_uz", "title_ru", "title_en", "link")
    prepopulated_fields = {"slug": ("title_en",)}
    fieldsets = (
        (None, {"fields": ("slug", "link", "status", "is_founder", "order", "is_active")}),
        ("O'zbekcha", {"fields": ("title_uz", "desc_uz")}),
        ("Русский", {"fields": ("title_ru", "desc_ru")}),
        ("English", {"fields": ("title_en", "desc_en")}),
    )

    @admin.display(description="Sayt")
    def site(self, obj):
        if not obj.link:
            return "—"
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', obj.link, obj.domain)


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


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("full_name",)}),
        ("Men haqimda", {"fields": ("about_uz", "about_ru", "about_en")}),
        ("Hozirgi holat (hero)", {"fields": ("now_uz", "now_ru", "now_en", "now_project")}),
    )

    def has_add_permission(self, request):
        return not SiteProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
