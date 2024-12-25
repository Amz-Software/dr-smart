from django import forms
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import User
from vendas.models import Loja

class LoginForm(AuthenticationForm):
    loja = forms.ModelChoiceField(queryset=Loja.objects.all(), required=True, label='Loja')
    
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }