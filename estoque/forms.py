from django.forms import inlineformset_factory, modelformset_factory
from estoque.models import EntradaEstoque
from django import forms
from .models import *


class EntradaEstoqueForm(forms.ModelForm):
    class Meta:
        model = EntradaEstoque
        fields = ['fornecedor', 'data_entrada', 'numero_nota']
        
        widgets = {
            'data_entrada': forms.DateInput(attrs={'type': 'date'}),
        }


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'telefone', 'email']

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, disabled=False, **kwargs):
        self.user = kwargs.pop('user', None)  # Pega o usuário que será passado pela view
        super().__init__(*args, **kwargs)
        if disabled:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:  
            if not instance.pk: 
                instance.criado_por = self.user
            instance.modificado_por = self.user 
        if commit:
            instance.save()
        return instance


class ProdutoEntradaForm(forms.ModelForm):
    class Meta:
        model = ProdutoEntrada
        exclude = ['loja', 'entrada', 'id']

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
    exclude=['entrada', 'loja'],
    extra=1,
    can_delete=False
)