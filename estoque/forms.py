from django.forms import inlineformset_factory, modelformset_factory
from estoque.models import EntradaEstoque
from django import forms
from .models import EntradaEstoque, EstoqueImei, ProdutoEntrada


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

class EstoqueImeiForm(forms.ModelForm):
    class Meta:
        model = EstoqueImei
        fields = ['imei', 'vendido', 'produto']
        #deve ser possivel editar a venda?
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendido'].widget.attrs.update({
            'class': 'form-check-input',  # Classe Bootstrap para o toggle switch
            })
        

ProdutoEntradaFormSet = modelformset_factory(
    ProdutoEntrada,
    exclude=['entrada'],
    extra=1,
    can_delete=False
)