from django.contrib.auth.views import LoginView, logout_then_login, PasswordResetView,PasswordResetView, PasswordResetDoneView,PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from vendas.models import Loja
from .forms import LoginForm


class LoginView(LoginView):
    template_name = 'login/login.html'
    authentication_form = LoginForm

    def form_valid(self, form):
        loja = form.cleaned_data.get('loja')
        user = form.get_user()
        if loja in user.lojas.all():
            self.request.session['loja_id'] = loja.id
            print(self.request.session['loja_id'])
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Você não tem permissão para acessar esta loja.')
            return redirect('accounts:login')
        

def logout_view(request):
    messages.success(request, 'Você saiu do sistema.')
    return logout_then_login(request)


class PasswordResetView(PasswordResetView):
    template_name = 'login/password_reset.html'
    email_template_name = 'login/password_reset_email.html'
    subject_template_name = 'login/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    title = 'Recuperar senha'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'login/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'login/password_reset_confirm.html'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'login/password_reset_complete.html'