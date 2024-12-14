from django import forms
from django.contrib.auth.forms import AuthenticationForm
from vendas.models import Loja

class LoginForm(AuthenticationForm):
    loja = forms.ModelChoiceField(queryset=Loja.objects.all(), required=True, label='Loja')