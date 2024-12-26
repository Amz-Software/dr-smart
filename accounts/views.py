from django.contrib.auth.views import LoginView, logout_then_login, PasswordResetView,PasswordResetView, PasswordResetDoneView,PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView
from vendas.models import Loja
from .forms import LoginForm
from django.views.generic.edit import UpdateView
from django.db.models import Q
from django.contrib.auth.models import Permission, Group
from .forms import UserForm
from .models import User


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
    

class MyProfileView(TemplateView):
    template_name = 'profile/my_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lojas'] = Loja.objects.all()
        return context
    

class MyProfileUpdateView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'profile/my_profile_update.html'
    success_url = reverse_lazy('accounts:my_profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lojas'] = Loja.objects.all()
        return context


class PermissionsListView(ListView):
    model = Permission
    template_name = 'auth/permissions_list.html'
    context_object_name = 'permissions'
    permission_required = 'auth.view_permission'
    paginate_by = 10
    
    def get_queryset(self):
        query = super().get_queryset()

        search = self.request.GET.get('search', None)
        if search:
            query = query.filter(Q(name__icontains=search) | Q(content_type__app_label__icontains=search)| Q(codename__icontains=search))

        return query

class GroupListView(ListView):
    model = Group
    template_name = 'auth/groups_list.html'
    context_object_name = 'groups'
    permission_required = 'auth.view_group'
    paginate_by = 10
    
class GroupCreateView(CreateView):
    model = Group
    fields = ['name', 'permissions']
    template_name = 'auth/group_form.html'
    success_url = reverse_lazy('accounts:group_list')
    permission_required = 'auth.add_group'
    
class GroupUpdateView(UpdateView):
    model = Group
    fields = ['name', 'permissions']
    template_name = 'auth/group_form.html'
    success_url = reverse_lazy('accounts:group_list')
    permission_required = 'auth.change_group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.object
        return context


class UserListView(ListView):
    model = User
    template_name = 'auth/users_list.html'
    context_object_name = 'users'
    permission_required = 'accounts.view_user'
    paginate_by = 10
    
    def get_queryset(self):
        query = super().get_queryset()

        search = self.request.GET.get('search', None)
        if search:
            query = query.filter(Q(username__icontains=search) | Q(email__icontains=search))

        return query