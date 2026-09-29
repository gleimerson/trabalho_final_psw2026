"""Rotas principais e arquivos enviados durante o desenvolvimento."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="listar_produtos"), name="inicio"),
    path("admin/", admin.site.urls),
    path("produtos/", include("produtos.urls")),
    path("pedidos/", include("pedidos.urls")),
    path("pessoas/", include("pessoa.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
