from django import forms
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import User
from vendas.models import Loja
from django.contrib.auth.models import Permission, Group
from django_select2.forms import Select2MultipleWidget

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class MyProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'password': forms.PasswordInput()
        }

    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        if first_name and last_name:
            username = f"{first_name.lower()}.{last_name.lower()}"
            cleaned_data['username'] = username
        return cleaned_data


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'permissions': Select2MultipleWidget()
        }