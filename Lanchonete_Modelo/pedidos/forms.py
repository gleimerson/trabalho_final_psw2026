from django import forms
from .models import Pedido, PedidoProduto

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['status', 'valor_total', 'pessoa']