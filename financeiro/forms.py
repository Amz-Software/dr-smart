# forms.py

from django import forms
from .models import GastoFixo, GastosAleatorios, Funcionario, CaixaMensal, CaixaMensalGastoFixo, CaixaMensalFuncionario

class GastosAleatoriosForm(forms.ModelForm):
    class Meta:
        model = GastosAleatorios
        fields = ['descricao', 'observacao', 'valor']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['nome', 'sobrenome', 'email', 'user']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

class GastoFixoForm(forms.ModelForm):
    class Meta:
        model = GastoFixo
        fields = ['nome']

class CaixaMensalGastoFixoForm(forms.ModelForm):
    class Meta:
        model = CaixaMensalGastoFixo
        fields = ['gasto_fixo', 'observacao', 'valor']
        widgets = {
            'gasto_fixo': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Certifique-se de que o queryset contém todos os Gastos Fixos
            self.fields['gasto_fixo'].queryset = GastoFixo.objects.all()

class CaixaMensalFuncionarioForm(forms.ModelForm):
    class Meta:
        model = CaixaMensalFuncionario
        fields = ['funcionario', 'comissao', 'salario']
        widgets = {
            'funcionario': forms.Select(attrs={'class': 'form-control'}),
            'comissao': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'salario': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

CaixaMensalFuncionarioFormSet = forms.modelformset_factory(CaixaMensalFuncionario, form=CaixaMensalFuncionarioForm, extra=0)
CaixaMensalGastoFixoFormSet = forms.modelformset_factory(CaixaMensalGastoFixo, form=CaixaMensalGastoFixoForm, extra=0)
GastosAleatoriosInlineForm = forms.inlineformset_factory(CaixaMensal, GastosAleatorios, form=GastosAleatoriosForm, extra=0)
