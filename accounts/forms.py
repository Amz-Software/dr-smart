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
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.instance.password)
        self.fields['password'].value = self.instance.password

    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'user_permissions', 'groups']
        widgets = {
            'password': forms.PasswordInput(),
            'user_permissions': Select2MultipleWidget(),
            'groups': Select2MultipleWidget()
        }
        
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'password': 'Senha',
            'user_permissions': 'Permissões',
            'groups': 'Grupos'
        }

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        if first_name and last_name:
            username = f"{first_name.lower()}.{last_name.lower()}"
            cleaned_data['username'] = username
        return cleaned_data
    
    #salvar usuário 
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'permissions': Select2MultipleWidget()
        }