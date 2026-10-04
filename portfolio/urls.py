from django.urls import path, register_converter

from . import views


class LangConverter:
    regex = "uz|ru|en"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(LangConverter, "lang")

app_name = "portfolio"

urlpatterns = [
    path("", views.root_redirect, name="root"),
    path("<lang:lang>/", views.index, name="index"),
    path("<lang:lang>/contact/", views.contact_submit, name="contact"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
]
