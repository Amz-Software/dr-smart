from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin

from vendas.models import Loja
from vendas.views import BaseView

def generate_views(modelo, form=None, paginacao=10, template_dir=''):
    """
    Gera as views baseadas no modelo e nos parâmetros fornecidos.
    
    :param modelo: Modelo do Django.
    :param form: Classe de formulário associada.
    :param paginacao: Número de itens por página na ListView.
    :param template_dir: Diretório onde os templates estão armazenados.
    :return: Dicionário contendo as views geradas.
    """

    class GeneratedListView(UserPassesTestMixin, ListView):
        model = modelo
        template_name = f'{template_dir}/{modelo._meta.model_name}_list.html'
        paginate_by = paginacao
        context_object_name = 'items'

        def test_func(self):
            return self.request.user.has_perm(f'{modelo._meta.app_label}.view_{modelo._meta.model_name}')

        def get_queryset(self):
            loja_id = self.request.session.get('loja_id')
            loja = get_object_or_404(Loja, pk=loja_id)
            search = self.request.GET.get('search')
            if search:
                return modelo.objects.filter(nome__icontains=search)
            return modelo.objects.filter(loja=loja)

    class GeneratedCreateView(UserPassesTestMixin, CreateView):
        model = modelo
        form_class = form
        template_name = f'{template_dir}/{modelo._meta.model_name}_create.html'
        success_url = f'/{modelo._meta.model_name}'
        
        def form_valid(self, form):
            form.instance.loja = Loja.objects.get(pk=self.request.session.get('loja_id'))
            return super().form_valid(form)

        def test_func(self):
            return self.request.user.has_perm(f'{modelo._meta.app_label}.add_{modelo._meta.model_name}')

        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['user'] = self.request.user
            return kwargs

    class GeneratedDetailView(UserPassesTestMixin, DetailView):
        model = modelo
        template_name = f'{template_dir}/{modelo._meta.model_name}_detail.html'
        context_object_name = modelo._meta.model_name

        def test_func(self):
            return self.request.user.has_perm(f'{modelo._meta.app_label}.view_{modelo._meta.model_name}')

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['form'] = form(instance=self.object, disabled=True) if form else None
            return context

    class GeneratedUpdateView(UserPassesTestMixin, UpdateView):
        model = modelo
        form_class = form
        template_name = f'{template_dir}/{modelo._meta.model_name}_edit.html'
        success_url = f'/{modelo._meta.model_name}'

        def test_func(self):
            return self.request.user.has_perm(f'{modelo._meta.app_label}.change_{modelo._meta.model_name}')

        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['user'] = self.request.user
            return kwargs

    class GeneratedDeleteView(UserPassesTestMixin, DeleteView):
        model = modelo
        success_url = reverse_lazy(f'{modelo._meta.model_name}s:{modelo._meta.model_name}s')

        def test_func(self):
            return self.request.user.has_perm(f'{modelo._meta.app_label}.delete_{modelo._meta.model_name}')

    return {
        'list_view': GeneratedListView,
        'create_view': GeneratedCreateView,
        'detail_view': GeneratedDetailView,
        'update_view': GeneratedUpdateView,
        'delete_view': GeneratedDeleteView
    }
