from decimal import Decimal

from django import forms
from django.db.models import Q
from django.forms import BaseInlineFormSet, inlineformset_factory

from pessoa.models import Pessoa
from produtos.models import Produto
from .models import Pedido, PedidoProduto


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ("pessoa", "status")

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        acao = "change" if self.instance.pk else "add"
        if not user.has_perm(f"pedidos.{acao}_pedido"):
            self.fields.pop("status")
            self.fields.pop("pessoa")
            if not self.instance.pk:
                self.instance.pessoa = Pessoa.objects.get(pk=user.pk)
        else:
            self.fields["pessoa"].queryset = Pessoa.objects.filter(is_active=True).order_by("nome")


class PedidoProdutoForm(forms.ModelForm):
    class Meta:
        model = PedidoProduto
        fields = ("produto", "quantidade")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["produto"].queryset = Produto.objects.filter(
            Q(disponivel=True) | Q(pk=self.instance.produto_id)
        ).order_by("nome")
        if self.instance.pk:
            self.fields["produto"].disabled = True
        self.fields["quantidade"].max_value = 10000
        self.fields["quantidade"].widget.attrs["max"] = 10000

    def clean(self):
        data = super().clean()
        produto = data.get("produto")
        quantidade = data.get("quantidade")
        if quantidade and quantidade > 10000:
            self.add_error("quantidade", "Informe no máximo 10000 unidades por item.")
        if produto:
            anterior = PedidoProduto.objects.filter(pk=self.instance.pk).first()
            mesmo_produto = anterior is not None and anterior.produto_id == produto.pk
            if not produto.disponivel and (not mesmo_produto or (quantidade or 0) > anterior.quantidade):
                self.add_error("produto", "Este produto não está disponível para novas unidades.")
            # O preço de uma linha existente é preservado ao mudar apenas a quantidade.
            self.instance.preco_unitario = anterior.preco_unitario if mesmo_produto else produto.preco
        return data


class BaseItensFormSet(BaseInlineFormSet):
    def clean(self):
        # Valide a identidade inclusive das linhas marcadas para exclusão.
        existentes = set(self.instance.itens.values_list("pk", flat=True)) if self.instance.pk else set()
        if self.initial_form_count() != len(existentes):
            raise forms.ValidationError("A lista de itens mudou. Recarregue a página e tente novamente.")
        enviados = set()
        for indice, form in enumerate(self.forms):
            item = form.cleaned_data.get("id")
            if indice < self.initial_form_count():
                if item is None or item.pk not in existentes or item.pk in enviados:
                    raise forms.ValidationError("Os itens informados não pertencem a este pedido ou estão repetidos.")
                enviados.add(item.pk)
            elif item is not None:
                raise forms.ValidationError("Um novo item não pode informar o ID de um item existente.")
        if existentes != enviados:
            raise forms.ValidationError("A lista de itens mudou. Recarregue a página e tente novamente.")
        super().clean()
        if any(self.errors):
            return
        total = Decimal("0.00")
        produtos = set()
        for form in self.forms:
            data = form.cleaned_data
            if not data or data.get("DELETE"):
                continue
            produto = data.get("produto")
            if produto:
                if produto.pk in produtos:
                    raise forms.ValidationError("Informe cada produto uma vez e ajuste sua quantidade.")
                produtos.add(produto.pk)
                total += form.instance.preco_unitario * data["quantidade"]
        if total > Decimal("9999999999.99"):
            raise forms.ValidationError("O total do pedido ultrapassa o limite permitido.")


PedidoProdutoFormSet = inlineformset_factory(
    Pedido, PedidoProduto, form=PedidoProdutoForm, formset=BaseItensFormSet,
    extra=1, can_delete=True, min_num=1, validate_min=True,
    max_num=100, validate_max=True, absolute_max=200,
)
