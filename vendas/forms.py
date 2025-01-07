from django import forms
from django.db.models import Subquery, OuterRef, Exists
from accounts.models import User
from estoque.models import Estoque, EstoqueImei
from produtos.models import Produto
from .models import Cliente, ContatoAdicional, Endereco, ComprovantesCliente, Loja, Pagamento, TipoPagamento, TipoEntrega, TipoVenda, Venda, ProdutoVenda
from django_select2.forms import Select2Widget, ModelSelect2Widget
from django_select2 import forms as s2forms


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        exclude = ['comprovantes', 'contato_adicional', 'loja']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'nascimento': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_cred_facil': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ContatoAdicionalForm(forms.ModelForm):
    class Meta:
        model = ContatoAdicional
        fields = '__all__'
        exclude = ['cliente', 'loja']
        widgets = {
            'nome_adicional': forms.TextInput(attrs={'class': 'form-control'}),
            'contato': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = '__all__'
        exclude = ['loja']
        widgets = {
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ComprovantesClienteForm(forms.ModelForm):
    class Meta:
        model = ComprovantesCliente
        fields = '__all__'
        exclude = ['cliente', 'loja']
        widgets = {
            'documento_identificacao_frente': forms.FileInput(attrs={'class': 'form-control'}),
            'documento_identificacao_verso': forms.FileInput(attrs={'class': 'form-control'}),
            'comprovante_residencia': forms.FileInput(attrs={'class': 'form-control'}),
            'consulta_serasa': forms.FileInput(attrs={'class': 'form-control'}),
        }

class TipoPagamentoForm(forms.ModelForm):
    class Meta:
        model = TipoPagamento
        fields = '__all__'
        exclude= ['loja']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'caixa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'parcelas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'financeira': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'caixa': 'Esse pagamento será realizado no caixa nas formas de recebimento pelo logista.',
            'parcelas': 'Marque se o pagamento pode ser parcelado.',
            'financeira': 'Marque se o pagamento é feito por financeira.',
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

class TipoEntregaForm(forms.ModelForm):
    class Meta:
        model = TipoEntrega
        fields = '__all__'
        exclude= ['loja']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
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

class TipoVendaForm(forms.ModelForm):
    class Meta:
        model = TipoVenda
        fields = '__all__'
        exclude= ['loja']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
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
    
class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = '__all__'
        exclude = ['loja','criado_por', 'modificado_por', 'caixa', 'produtos', 'loja']

        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'vendedor': forms.Select(attrs={'class': 'form-control'}),
            'tipo_venda': forms.Select(attrs={'class': 'form-control'}),
            'tipo_entrega': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
        labels = {
            'cliente': 'Cliente',
            'vendedor': 'Vendedor',
            'tipo_venda': 'Tipo de Venda',
            'tipo_entrega': 'Tipo de Entrega',
            'observacao': 'Observação',
        }

class EstoqueImeiSelectWidget(ModelSelect2Widget):
    search_fields = ['imei__icontains', 'produto__nome__icontains']
    


class ProdutoVendaForm(forms.ModelForm):
    valor_total = forms.DecimalField(label='Valor Total', disabled=True, required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    imei = forms.ModelChoiceField(
        queryset=EstoqueImei.objects.filter(vendido=False),
        label='imei',
        required=False,
        empty_label='Digite o IMEI ou o nome do produto',
        widget=EstoqueImeiSelectWidget(attrs={'class': 'form-control'})
    )
    class Meta:
        model = ProdutoVenda
        fields = '__all__'
        exclude = ['loja', 'venda']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_desconto': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'valor_unitario': 'Valor',
            'valor_desconto': 'Desconto',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas os produtos que estão em estoque (quantidade >  0)
        self.fields['produto'].queryset = Produto.objects.filter(
            Exists(
                Estoque.objects.filter(
                    produto=OuterRef('pk'),
                    quantidade_disponivel__gt=0
                )
            )
        )


class PagamentoForm(forms.ModelForm):
    valor_parcela = forms.DecimalField(label='Valor Parcela', disabled=True, required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    class Meta:
        model = Pagamento
        fields = '__all__'
        exclude = ['venda', 'loja']
        widgets = {
            'tipo_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'parcelas': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_primeira_parcela': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

FormaPagamentoFormSet = forms.inlineformset_factory(Venda, Pagamento, form=PagamentoForm, extra=1, can_delete=False)
ProdutoVendaFormSet = forms.inlineformset_factory(Venda, ProdutoVenda, form=ProdutoVendaForm, extra=1, can_delete=False)


from django_select2.forms import Select2MultipleWidget


class LojaForm(forms.ModelForm):
    class Meta:
        model = Loja
        fields = '__all__'
        widgets = {
            'usuarios': Select2MultipleWidget(attrs={'class': 'form-control'}),
        }

    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'form-control'}),
        required=False
    )