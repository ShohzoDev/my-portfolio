from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from portfolio.security import throttled_admin_login

admin.site.site_header = "Shohzod — portfolio boshqaruvi"
admin.site.site_title = "Portfolio admin"
admin.site.index_title = "Boshqaruv paneli"

urlpatterns = [
    # Must come before admin.site.urls so it shadows the stock login view.
    path(f"{settings.ADMIN_URL}login/", throttled_admin_login, name="admin_login_throttled"),
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("portfolio.urls")),
]

if settings.DEBUG:
    # Uploaded project covers in local development. In production nginx (or
    # PythonAnywhere's "Static files" tab) serves /media/ directly.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
