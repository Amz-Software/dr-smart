from django import forms
from django_select2.forms import Select2MultipleWidget, Select2Widget
from estoque.models import Estoque
from produtos.models import Produto
from vendas.models import Cliente
from .models import CaixaAssistencia, OrdemServico, PecaOrdemServico

class CaixaAssistenciaForm(forms.ModelForm):
    class Meta:
        model = CaixaAssistencia
        fields = ['data_abertura', 'data_fechamento']
        widgets = {
            'data_abertura': forms.DateInput(attrs={'type': 'date'}),
            'data_fechamento': forms.DateInput(attrs={'type': 'date'}),
        }

class OrdemServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = '__all__'
        exclude = ['loja', 'criado_por', 'modificado_por', 'pecas']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control select2'}),
            'data_entrada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'aparelho': forms.TextInput(attrs={'class': 'form-control'}),
            'defeito_relato': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'mao_de_obra': forms.TextInput(attrs={'class': 'form-control money'}),
            'valor_servico': forms.TextInput(attrs={'class': 'form-control money'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control'}),
            'data_finalizacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'cliente': 'Cliente',
            'aparelho': 'Aparelho',
            'defeito_relato': 'Defeito Relatado',
            'status': 'Status',
            'mao_de_obra': 'Mão de Obra',
            'valor_servico': 'Valor do Serviço',
            'observacoes': 'Observações',
            'data_finalizacao': 'Data de Finalização',
        }

    def __init__(self, *args, **kwargs):
        loja = kwargs.pop('loja', None)
        super().__init__(*args, **kwargs)
        if loja:
            self.fields['cliente'].queryset = Cliente.objects.filter(loja=loja)
        else:
            self.fields['cliente'].queryset = Cliente.objects.none()

class PecaOrdemServicoForm(forms.ModelForm):
    class Meta:
        model = PecaOrdemServico
        fields = ['produto', 'quantidade', 'valor_unitario']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control select2'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_unitario': forms.TextInput(attrs={'class': 'form-control money'}),
        }
        labels = {
            'produto': 'Produto',
            'quantidade': 'Quantidade',
            'valor_unitario': 'Valor Unitário',
        }

    def __init__(self, *args, **kwargs):
        loja = kwargs.pop('loja', None)
        super().__init__(*args, **kwargs)
        if loja:
            self.fields['produto'].queryset = Produto.objects.filter(
                estoque_atual__loja=loja, 
                estoque_atual__quantidade_disponivel__gt=0, 
                tipo__assistencia=True
            ).distinct()
        else:
            self.fields['produto'].queryset = Produto.objects.none()

pecas_inline_formset = forms.inlineformset_factory(
    OrdemServico,
    PecaOrdemServico,
    form=PecaOrdemServicoForm,
    extra=1,
    can_delete=True
)