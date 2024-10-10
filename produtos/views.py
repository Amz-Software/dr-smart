from typing import Any
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from produtos.forms import ProdutoForms
from produtos.models import Produto

class ProdutoListView(ListView):
    model = Produto
    template_name = 'produtos/produtos.html'
    paginate_by = 10
    context_object_name = 'produtos'

    def get_queryset(self):
        search = self.request.GET.get('search')
        if search:
            return Produto.objects.filter(nome__icontains=search)
        return Produto.objects.all()

class ProdutoCreateView(CreateView):
    model = Produto
    form_class = ProdutoForms
    template_name = 'produtos/produto_create.html'
    success_url = '/produtos'

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # Passa o usuário para o formulário
        return kwargs

class ProdutoDetailView(DetailView):
    model = Produto
    template_name = 'produtos/produto_detail.html'
    context_object_name = 'produto'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = ProdutoForms(instance=self.object, disabled=True)
        return context

class ProdutoUpdateView(UpdateView):
    model = Produto
    form_class = ProdutoForms
    template_name = 'produtos/produto_edit.html'
    success_url = '/produtos'

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class ProdutoDeleteView(DeleteView):
    model = Produto
    success_url = reverse_lazy('produtos:produtos')