from django import forms
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import User
from vendas.models import Loja

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
    
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }