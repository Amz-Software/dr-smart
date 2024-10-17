from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from estoque.forms import EntradaForm
from estoque.models import EntradaEstoque, Estoque
from django.contrib import messages

class EstoqueListView(ListView):
    model = Estoque
    template_name = 'estoque/estoque_list.html'
    context_object_name = 'produtos'
    
    def get_queryset(self):
        query = super().get_queryset()
        
        search = self.request.GET.get('search', None)
        if search:
            query = query.filter(produto__nome__icontains=search)
            
        return query

class EstoqueCreateView(CreateView):
    model = EntradaEstoque
    template_name = 'estoque/estoque_form.html'
    form_class = EntradaForm
    success_url = reverse_lazy('estoque:estoque_list')
    
    def form_valid(self, form):
        estoque = form.save(commit=False)
        messages.success(self.request, f"Estoque de {estoque.produto.nome} atualizado.")
        return super().form_valid(form)