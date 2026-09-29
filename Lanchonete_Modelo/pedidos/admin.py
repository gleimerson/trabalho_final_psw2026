from django.contrib import admin

from .forms import BaseItensFormSet, PedidoProdutoForm
from .models import Pedido, PedidoProduto


class PedidoProdutoInline(admin.TabularInline):
    model = PedidoProduto
    form = PedidoProdutoForm
    formset = BaseItensFormSet
    fields = ("produto", "quantidade", "preco_unitario")
    readonly_fields = ("preco_unitario",)
    extra = 1
    min_num = 1
    max_num = 100

    def get_formset(self, request, obj=None, **kwargs):
        kwargs.update(validate_min=True, validate_max=True, absolute_max=200)
        return super().get_formset(request, obj, **kwargs)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "pessoa", "status", "valor_total", "data_pedido")
    list_filter = ("status", "data_pedido")
    list_select_related = ("pessoa",)
    search_fields = ("pessoa__nome", "pessoa__username")
    readonly_fields = ("valor_total", "data_pedido")
    inlines = (PedidoProdutoInline,)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalcular_total()
