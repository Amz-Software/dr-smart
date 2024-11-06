from django import forms
from .models import Cliente, ContatoAdicional, Endereco, ComprovantesCliente, Pagamento, TipoPagamento, TipoEntrega, TipoVenda, Venda, ProdutoVenda


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        exclude = ['comprovantes', 'contato_adicional']
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
        exclude = ['cliente']
        widgets = {
            'nome_adicional': forms.TextInput(attrs={'class': 'form-control'}),
            'contato': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = '__all__'
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
        exclude = ['cliente']
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
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'caixa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'parcelas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'financeira': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
        exclude = ['criado_por', 'modificado_por', 'caixa']

        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'vendedor': forms.Select(attrs={'class': 'form-control'}),
            'tipo_venda': forms.Select(attrs={'class': 'form-control'}),
            'tipo_entrega': forms.Select(attrs={'class': 'form-control'}),
            'produtos': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

ProdutoVendaFormSet = forms.inlineformset_factory(Venda, ProdutoVenda, fields=['produto', 'valor_unitario', 'quantidade'], extra=1)
FormaPagamentoFormSet = forms.inlineformset_factory(Venda, Pagamento, fields=['tipo_pagamento', 'valor', 'parcelas', 'data_primeira_parcela'], extra=1)