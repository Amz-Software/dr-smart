from typing import Any
from django import forms

from produtos.models import *


class ProdutoForms(forms.ModelForm):
    class Meta:
        model = Produto
        fields = '__all__'
        exclude = ['loja', 'criado_por', 'modificado_por']
        labels = {
            'codigo': 'Código',
            'nome': 'Nome',
            'tipo': 'Tipo',
            'fabricante': 'Fabricante',
            'cor': 'Cor',
            'memoria': 'Memória',
            'estado': 'Estado',
        }
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'fabricante': forms.Select(attrs={'class': 'form-control'}),
            'cor': forms.Select(attrs={'class': 'form-control'}),
            'memoria': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
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
    
class CorProdutoForms(forms.ModelForm):
    class Meta:
        model = CorProduto
        fields = '__all__'
        exclude = ['loja', 'criado_por', 'modificado_por']
        labels = {
            'nome': 'Nome',
        }
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
    
class TipoForms(forms.ModelForm):
    class Meta:
        model = TipoProduto
        fields = '__all__'
        exclude = ['loja', 'criado_por', 'modificado_por']
        labels = {
            'nome': 'Nome',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, disabled=False, **kwargs):
        self.user = kwargs.pop('user', None)  # Pega o usuário que será passado pela view
        # caso o usario tenha permissao mostrar o campo assistencia
        super().__init__(*args, **kwargs)
        if self.user and self.user.has_perm('assistencia.view_assistencia'):
            self.fields['assistencia'].widget.attrs['disabled'] = False
        else:
            self.fields['assistencia'].widget.attrs['disabled'] = True
        # caso o usuario tenha permissao mostrar o campo assistencia
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
    
class FabricanteForms(forms.ModelForm):
    class Meta:
        model = Fabricante
        fields = '__all__'
        exclude = ['loja', 'criado_por', 'modificado_por']
        labels = {
            'nome': 'Nome',
        }
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
    
class MemoriaForms(forms.ModelForm):
    class Meta:
        model = MemoriaProduto
        fields = '__all__'
        exclude = ['loja', 'criado_por', 'modificado_por']
        labels = {
            'nome': 'Nome',
        }
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
    
class EstadoProdutoForms(forms.ModelForm):
    class Meta:
        model = EstadoProduto
        fields = '__all__'
        exclude = ['loja', 'criado_por', 'modificado_por']
        labels = {
            'nome': 'Nome',
        }
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