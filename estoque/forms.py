from estoque.models import EntradaEstoque
from django import forms


class EntradaForm(forms.ModelForm):
    class Meta:
        model = EntradaEstoque
        fields = ['fornecedor', 'data_entrada', 'numero_nota', 'produto', 'imei', 'custo_unitario', 'venda_unitaria', 'quantidade']
        widgets = {
            'data_entrada': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }