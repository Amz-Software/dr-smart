from django import forms
from django.db.models import Subquery, OuterRef, Exists
from accounts.models import User
from estoque.models import Estoque, EstoqueImei
from produtos.models import Produto
from .models import *
from django_select2.forms import Select2Widget, ModelSelect2Widget, Select2MultipleWidget
from django_select2.forms import ModelSelect2MultipleWidget, HeavySelect2Widget
from decimal import Decimal

class EstoqueImeiSelectWidgetEdit(HeavySelect2Widget):
    data_view = 'estoque:estoque-imei-search-edit'
    
    def render(self, name, value, attrs=None, renderer=None):
        # Se houver um valor, insere a opção inicial no HTML
        initial_options = []
        if value:
            try:
                imei_obj = self.get_queryset().get(pk=value)
                # Monta o texto da opção igual ao utilizado na view de busca
                text = f'{imei_obj.imei} - {imei_obj.produto.nome} - {imei_obj.vendido}'
                initial_options = [(imei_obj.pk, text)]
                # Se desejar, pode inserir também um atributo no select para uso no JS:
                if attrs is None:
                    attrs = {}
                attrs['data-initial-text'] = text
            except Exception:
                initial_options = [(value, value)]
        
        # Armazena as opções originais (se houver)
        original_choices = list(self.choices)
        # Mescla a opção inicial com as demais
        choices = initial_options + original_choices
        self.choices = choices
        rendered = super().render(name, value, attrs, renderer)
        # Restaura as opções originais para evitar efeitos colaterais
        self.choices = original_choices
        return rendered


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
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'uf': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_cred_facil': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome': 'Nome*',
            'email': 'Email',
            'telefone': 'Telefone',
            'cpf': 'CPF*',
            'nascimento': 'Data de Nascimento*',
            'rg': 'RG',
            'cep': 'CEP',
            'bairro': 'Bairro',
            'endereco': 'Endereço',
            'cidade': 'Cidade',
            'uf': 'UF',
            'cliente_cred_facil': 'Cliente Crédito Fácil',
        }

class ContatoAdicionalForm(forms.ModelForm):
    class Meta:
        model = ContatoAdicional
        fields = '__all__'
        exclude = ['cliente', 'loja']
        widgets = {
            'nome_adicional': forms.TextInput(attrs={'class': 'form-control'}),
            'contato': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_adicional': forms.TextInput(attrs={'class': 'form-control'}),
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
            'carne': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nao_contabilizar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'caixa': 'Esse pagamento será realizado no caixa nas formas de recebimento pelo logista.',
            'parcelas': 'Marque se o pagamento pode ser parcelado.',
            'financeira': 'Marque se o pagamento é feito por financeira.',
            'carne': 'Marque se o pagamento é feito por carnê ou promissória.',
            'nao_contabilizar': 'Marque se o pagamento não deve ser contabilizado.',
        }
        labels = {
            'nome': 'Nome*',
            'caixa': 'Caixa',
            'parcelas': 'Parcelas',
            'financeira': 'Financeira',
            'carne': 'Carnê',
            'nao_contabilizar': 'Não Contabilizar',
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
            'cliente': 'Cliente*',
            'vendedor': 'Vendedor*',
            'tipo_venda': 'Tipo de Venda*',
            'tipo_entrega': 'Tipo de Entrega*',
            'observacao': 'Observação',
        }

    def __init__(self, *args, **kwargs):
        loja = kwargs.pop('loja', None)  # Captura o argumento 'loja'
        user = kwargs.pop('user', None)  # Captura o argumento 'user'
        super().__init__(*args, **kwargs) 
        if loja:
            self.fields['cliente'].queryset = Cliente.objects.filter(loja=loja)
            self.fields['vendedor'].queryset = Loja.objects.get(id=loja).usuarios.all()
            self.fields['tipo_venda'].queryset = TipoVenda.objects.filter(loja=loja)
            self.fields['tipo_entrega'].queryset = TipoEntrega.objects.filter(loja=loja)
        if user:
            self.fields['vendedor'].initial = user


class EstoqueImeiSelectWidget(HeavySelect2Widget):
    data_view = 'estoque:estoque-imei-search'

class ProdutoSelectWidget(HeavySelect2Widget):
    data_view = 'vendas:produtos_ajax'


class ProdutoVendaForm(forms.ModelForm):
    valor_total = forms.DecimalField(
        label='Valor Total',
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control money',
            'readonly': 'readonly',
            'width': '100%'
        })
    )
    imei = forms.ModelChoiceField(
        queryset=EstoqueImei.objects.filter(vendido=False),
        label='imei',
        required=False,
        widget=EstoqueImeiSelectWidget(
            max_results=10,
            attrs={
                'class': 'form-control',
                'data-minimum-input-length': '0',
                'data-placeholder': 'Selecione um IMEI',
                'data-allow-clear': 'true',
            }
        )
    )
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.all(),
        label="Produto",
        widget=ProdutoSelectWidget(
            max_results=10,
            attrs={
                'class': 'form-control',
                'data-minimum-input-length': '0',
                'data-placeholder': 'Selecione um produto',
                'data-allow-clear': 'true',
            },
        )
    )

    class Meta:
        model = ProdutoVenda
        fields = '__all__'
        exclude = ['loja', 'venda']
        widgets = {
            'valor_unitario': forms.TextInput(attrs={'class': 'form-control money'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_desconto': forms.TextInput(attrs={'class': 'form-control money'}),
        }
        labels = {
            'valor_unitario': 'Valor*',
            'valor_desconto': 'Desconto*',
            'quantidade': 'Quantidade*',
            'produto': 'Produto*',
        }

    def __init__(self, *args, **kwargs):
        loja = kwargs.pop('loja', None)
        super().__init__(*args, **kwargs)
        # Filtra apenas os produtos que estão em estoque (quantidade > 0)
        self.fields['produto'].queryset = Produto.objects.filter(
            Exists(
                Estoque.objects.filter(
                    produto=OuterRef('pk'),
                    quantidade_disponivel__gt=0
                )
            )
        ).filter(loja=loja)
        self.fields['imei'].queryset = EstoqueImei.objects.filter(vendido=False).filter(produto__loja=loja)
        
        
class ProdutoVendaEditForm(forms.ModelForm):
    valor_total = forms.DecimalField(
        label='Valor Total',
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control money', 'readonly': 'readonly'})
    )
    # quero apenas o produto que está na venda
    produto = forms.ModelChoiceField(
        queryset=None,
        label="Produto",
    )

    class Meta:
        model = ProdutoVenda
        fields = '__all__'
        exclude = ['loja', 'venda']
        widgets = {
            'valor_unitario': forms.TextInput(attrs={'class': 'form-control money'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_desconto': forms.TextInput(attrs={'class': 'form-control money'}),
            'imei': EstoqueImeiSelectWidgetEdit(
                max_results=10,
                attrs={
                    'class': 'form-control',
                    'data-minimum-input-length': '0',
                    'data-placeholder': 'Selecione um IMEI',
                    'data-allow-clear': 'true',
                }
            )
        }
        labels = {
            'valor_unitario': 'Valor*',
            'valor_desconto': 'Desconto*',
            'quantidade': 'Quantidade*', 
            'produto': 'Produto*',
        }
    
    def __init__(self, *args, **kwargs):
        loja = kwargs.pop('loja', None)
        super().__init__(*args, **kwargs)
        self.fields['produto'].queryset = Produto.objects.filter(loja=loja).filter(id=self.instance.produto.id)



class PagamentoForm(forms.ModelForm):
    valor_parcela = forms.DecimalField(label='Valor Parcela', disabled=True, required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    class Meta:
        model = Pagamento
        fields = '__all__'
        exclude = ['venda', 'loja']
        widgets = {
            'tipo_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.TextInput(attrs={'class': 'form-control money'}),
            'parcelas': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_primeira_parcela': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}),
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
            # ajustar data da primeira parcela para o padrao yyyy-MM-dd
            self.fields['data_primeira_parcela'].widget.format = '%Y-%m-%d'

class LancamentoForm(forms.ModelForm):
    class Meta:
        model = LancamentoCaixa
        fields = '__all__'
        exclude = ['loja', 'caixa']
        widgets = {
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_lancamento': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.TextInput(attrs={'class': 'form-control money'}),
        }
        labels = {
            'motivo': 'Motivo*',
            'tipo_lancamento': 'Tipo de Lançamento*',
            'valor': 'Valor*',
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
        
class LancamentoCaixaTotalForm(forms.ModelForm):
    class Meta:
        model = LancamentoCaixaTotal
        fields = '__all__'
        exclude = ['loja', 'caixa']
        widgets = {
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_lancamento': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.TextInput(attrs={'class': 'form-control money'}),
        }
        labels = {
            'motivo': 'Motivo*',
            'tipo_lancamento': 'Tipo de Lançamento*',
            'valor': 'Valor*',
        }

FormaPagamentoFormSet = forms.inlineformset_factory(Venda, Pagamento, form=PagamentoForm, extra=1, can_delete=False)
ProdutoVendaFormSet = forms.inlineformset_factory(Venda, ProdutoVenda, form=ProdutoVendaForm, extra=1, can_delete=False)

FormaPagamentoEditFormSet = forms.inlineformset_factory(Venda, Pagamento, form=PagamentoForm, extra=0, can_delete=True)
ProdutoVendaEditFormSet = forms.inlineformset_factory(Venda, ProdutoVenda, form=ProdutoVendaEditForm, extra=0, can_delete=True)


class UsuarioSelectWidget(ModelSelect2MultipleWidget):
    search_fields = [
        'username__icontains', 
        'first_name__icontains', 
        'last_name__icontains'
    ]

class LojaForm(forms.ModelForm):
    class Meta:
        model = Loja
        fields = '__all__'

    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=UsuarioSelectWidget(attrs={'class': 'form-control'}),
        required=False
    )

    gerentes = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=UsuarioSelectWidget(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        # Recupera o ID da loja passada como parâmetro
        user_loja_id = kwargs.pop('user_loja', None)
        super().__init__(*args, **kwargs)
        # Define o valor inicial do campo 'loja' se o ID foi fornecido
        if user_loja_id:
            self.fields['loja'].initial = Loja.objects.get(id=user_loja_id)

    def save(self, commit=True):
        # Obtém a instância sem salvar imediatamente
        instance = super().save(commit=False)
        # Atribui o valor da loja ao objeto salvo
        if not instance.loja:
            instance.loja = self.fields['loja'].initial
        # Salva a instância, se necessário
        if commit:
            instance.save()
            self.save_m2m()
        return instance
    
    
class RelatorioVendasForm(forms.Form):
    data_inicial = forms.DateField(
        label='Data Inicial',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_final = forms.DateField(
        label='Data Final',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    produtos = forms.ModelMultipleChoiceField(
        queryset=Produto.objects.all(),
        label='Produtos',
        required=False,
        widget=Select2MultipleWidget(attrs={'class': 'form-control'})
    )
    cliente = forms.ModelMultipleChoiceField(
        queryset=Cliente.objects.all(),
        label='Clientes',
        required=False,
        widget=Select2MultipleWidget(attrs={'class': 'form-control'})
    )
    vendedores = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        label='Vendedores',
        required=False,
        widget=Select2MultipleWidget(attrs={'class': 'form-control'})
    )
    lojas = forms.ModelMultipleChoiceField(
        queryset=Loja.objects.all(),
        label='Lojas',
        required=False,
        widget=Select2MultipleWidget(attrs={'class': 'form-control'})
    )
    tipos_venda = forms.ModelMultipleChoiceField(
        queryset=TipoPagamento.objects.all().distinct(),
        label='Tipos de Pagamento',
        required=False,
        widget=Select2MultipleWidget(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        loja = kwargs.pop('loja', None)
        print(f'Loja no form: {loja}')
        super().__init__(*args, **kwargs)
        if loja:
            self.fields['produtos'].queryset = Produto.objects.filter(loja=loja)
            self.fields['cliente'].queryset = Cliente.objects.filter(loja=loja)
            self.fields['vendedores'].queryset = User.objects.filter(loja=loja)
            self.fields['lojas'].queryset = Loja.objects.filter(id=loja)
            self.fields['tipos_venda'].queryset = TipoPagamento.objects.filter(loja=loja)

            self.fields['lojas'].initial = loja

