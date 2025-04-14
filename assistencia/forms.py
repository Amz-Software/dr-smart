from django import forms
from django_select2.forms import Select2MultipleWidget
from estoque.models import Estoque
from produtos.models import Produto
from .models import CaixaAssistencia, OrdemServico

class CaixaAssistenciaForm(forms.ModelForm):
    class Meta:
        model = CaixaAssistencia
        fields = ['data_abertura', 'data_fechamento']
        widgets = {
            'data_abertura': forms.DateInput(attrs={'type': 'date'}),
            'data_fechamento': forms.DateInput(attrs={'type': 'date'}),
        }

class OrdemServicoForm(forms.ModelForm):
    pecas = forms.ModelMultipleChoiceField(
        queryset=Produto.objects.none(),
        label='Peças',
        widget=Select2MultipleWidget(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = OrdemServico
        fields = '__all__'
        exclude = ['loja', 'criado_por', 'modificado_por']
        widgets = {
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
            self.fields['pecas'].queryset = Produto.objects.filter(
                estoque_atual__loja=loja, 
                estoque_atual__quantidade_disponivel__gt=0, 
                tipo__assistencia=True
            ).distinct()
        else:
            self.fields['pecas'].queryset = Produto.objects.none()
