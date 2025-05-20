from django import forms
from django_select2.forms import Select2MultipleWidget, Select2Widget
from estoque.models import Estoque
from produtos.models import Produto
from vendas.models import Cliente, TipoPagamento
from .models import CaixaAssistencia, OrdemServico, PecaOrdemServico, PagamentoAssistencia, ParcelaAssistencia

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
            'valor_servico': forms.TextInput(attrs={
            'class': 'form-control money',
            'readonly': 'readonly',
            'style': 'background-color: #d4edda;'  # verde claro
            }),
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
    extra=0,
    can_delete=True
)


class PagamentoAssistenciaForm(forms.ModelForm):
    valor_parcela = forms.DecimalField(
        label='Valor Parcela', disabled=True, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta:
        model = PagamentoAssistencia
        fields = '__all__'
        exclude = ['ordem_servico', 'loja']
        widgets = {
            'tipo_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.TextInput(attrs={'class': 'form-control money'}),
            'parcelas': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_primeira_parcela': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'tipo_pagamento': 'Tipo de Pagamento*',
            'valor': 'Valor*',
            'parcelas': 'Parcelas*',
            'data_primeira_parcela': 'Data Primeira Parcela*',
        }

    def __init__(self, *args, **kwargs):
        loja = kwargs.pop('loja', None)
        super().__init__(*args, **kwargs)
        if loja:
            self.fields['tipo_pagamento'].queryset = TipoPagamento.objects.filter(loja=loja)
            # ajusta formato de data para yyyy-MM-dd
            self.fields['data_primeira_parcela'].widget.format = '%Y-%m-%d'

class ParcelaAssistenciaForm(forms.ModelForm):
    class Meta:
        model = ParcelaAssistencia
        fields = ['numero_parcela', 'valor', 'valor_pago', 'tipo_pagamento', 'desconto', 'data_vencimento', 'pago']
        widgets = {
            'numero_parcela': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor': forms.TextInput(attrs={'class': 'form-control money'}),
            'valor_pago': forms.TextInput(attrs={'class': 'form-control money'}),
            'tipo_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'desconto': forms.TextInput(attrs={'class': 'form-control money'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pago': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'numero_parcela': 'Número da Parcela',
            'valor': 'Valor',
            'valor_pago': 'Valor Pago',
            'tipo_pagamento': 'Tipo de Pagamento',
            'desconto': 'Desconto',
            'data_vencimento': 'Data de Vencimento',
            'pago': 'Pago',
        }

    def __init__(self, *args, **kwargs):
        super(ParcelaAssistenciaForm, self).__init__(*args, **kwargs)
        self.fields['tipo_pagamento'].queryset = TipoPagamento.objects.filter(loja=self.instance.pagamento.loja)

FormaPagamentoAssistenciaFormSet = forms.inlineformset_factory(
    OrdemServico,
    PagamentoAssistencia,
    form=PagamentoAssistenciaForm,
    extra=0,
    can_delete=False
)

FormaPagamentoAssistenciaEditFormSet = forms.inlineformset_factory(
    OrdemServico,
    PagamentoAssistencia,
    form=PagamentoAssistenciaForm,
    extra=0,
    can_delete=True
)

parcela_inline_formset = forms.inlineformset_factory(
    PagamentoAssistencia,
    ParcelaAssistencia,
    form=ParcelaAssistenciaForm,
    extra=0,
    can_delete=True
)