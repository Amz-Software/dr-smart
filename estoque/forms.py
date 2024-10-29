from django.forms import inlineformset_factory
from estoque.models import EntradaEstoque
from django import forms
from .models import EntradaEstoque, ProdutoEntrada


class EntradaEstoqueForm(forms.ModelForm):
    class Meta:
        model = EntradaEstoque
        fields = ['fornecedor', 'data_entrada', 'numero_nota']
        
        widgets = {
            'data_entrada': forms.DateInput(attrs={'type': 'date'}),
        }


class ProdutoEntradaForm(forms.ModelForm):
    class Meta:
        model = ProdutoEntrada
        exclude = ['entrada', 'id']

ProdutoEntradaFormSet = inlineformset_factory(
    EntradaEstoque, ProdutoEntrada, form=ProdutoEntradaForm, extra=1, can_delete=False
)
