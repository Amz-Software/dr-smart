# forms.py

from django import forms

from accounts.models import User
from .models import *
from vendas.models import *

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = '__all__'

class ParcelaForm(forms.ModelForm):
    class Meta:
        model = Parcela
        fields = '__all__'
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'readonly': 'readonly'}),
            'valor_pago': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'tipo_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'pago': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'numero_parcela': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'desconto': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ParcelaForm, self).__init__(*args, **kwargs)
        self.fields['tipo_pagamento'].queryset = TipoPagamento.objects.filter(loja=self.instance.pagamento.loja)

class GastosAleatoriosForm(forms.ModelForm):
    class Meta:
        model = GastosAleatorios
        fields = ['descricao', 'observacao', 'valor']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }
class GastoFixoForm(forms.ModelForm):
    class Meta:
        model = GastoFixo
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome do Gasto Fixo',
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

class CaixaMensalGastoFixoForm(forms.ModelForm):
    class Meta:
        model = CaixaMensalGastoFixo
        fields = ['gasto_fixo', 'observacao', 'valor']
        widgets = {
            'gasto_fixo': forms.Select(attrs={'class': 'form-select'}),
            'observacao': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(CaixaMensalGastoFixoForm, self).__init__(*args, **kwargs)
        self.fields['gasto_fixo'].queryset = GastoFixo.objects.filter(loja=self.instance.caixa_mensal.loja)


class CaixaMensalFuncionarioForm(forms.ModelForm):
    nome = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CaixaMensalFuncionario
        fields = ['comissao', 'salario']
        widgets = {
            'comissao': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'salario': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }
        labels = {
            'comissao': 'Comissão',
            'salario': 'Salário',
        }
    
    def __init__(self, *args, **kwargs):
        super(CaixaMensalFuncionarioForm, self).__init__(*args, **kwargs)
        # Preencher o campo nome com o nome do funcionário 
        self.fields['nome'].initial = f'{self.instance.funcionario.first_name} {self.instance.funcionario.last_name}'
        self.fields['nome'].widget.attrs['readonly'] = 'readonly'

# Definições dos FormSets com Prefixo
CaixaMensalGastoFixoFormSet = forms.modelformset_factory(
    CaixaMensalGastoFixo,
    form=CaixaMensalGastoFixoForm,
    extra=0
)

CaixaMensalFuncionarioFormSet = forms.modelformset_factory(
    CaixaMensalFuncionario,
    form=CaixaMensalFuncionarioForm,
    extra=0,
    can_delete=True
)

GastosAleatoriosFormSet = forms.inlineformset_factory(
    CaixaMensal,
    GastosAleatorios,
    form=GastosAleatoriosForm,
    extra=0,
    can_delete=True
)

ParcelaInlineFormSet = forms.inlineformset_factory(
    Pagamento,
    Parcela,
    form=ParcelaForm,
    extra=0,
    can_delete=True
)