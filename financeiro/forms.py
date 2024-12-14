# forms.py

from django import forms
from .models import GastosAleatorios

class GastosAleatoriosForm(forms.ModelForm):
    class Meta:
        model = GastosAleatorios
        fields = ['descricao', 'observacao', 'valor']
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 1}),
        }