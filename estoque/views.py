from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
# from estoque.forms import EntradaForm
from estoque.models import EntradaEstoque, Estoque, EstoqueImei, ProdutoEntrada
from django.contrib import messages
from django.forms import inlineformset_factory

from produtos.models import Produto
from .forms import EntradaEstoqueForm, ProdutoEntradaForm, ProdutoEntradaFormSet

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

# class EstoqueCreateView(CreateView):
#     model = EntradaEstoque
#     template_name = 'estoque/estoque_form.html'
#     form_class = EntradaForm
#     success_url = reverse_lazy('estoque:estoque_list')
    
#     def form_valid(self, form):
#         estoque = form.save(commit=False)
#         messages.success(self.request, f"Estoque de {estoque.produto.nome} atualizado.")
#         return super().form_valid(form)
    

class EntradaListView(ListView):
    model = EntradaEstoque
    template_name = 'estoque/estoque_entrada_list.html'
    context_object_name = 'entradas'
    
    def get_queryset(self):
        query = super().get_queryset()
        
        search = self.request.GET.get('search', None)
        if search:
            query = query.filter(fornecedor__nome__icontains=search)
            
        return query

class EntradaEstoqueCreateView(CreateView):
    model = EntradaEstoque
    form_class = EntradaEstoqueForm
    template_name = 'estoque/estoque_form.html'
    
    def get_success_url(self):
        return reverse_lazy('estoque:estoque_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProdutoEntradaFormSet(self.request.POST)
        else:
            context['formset'] = ProdutoEntradaFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            print(form)
            print(formset)
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)
        
class AdicionarEntradaEstoqueView(CreateView):
    model = EntradaEstoque
    form_class = EntradaEstoqueForm
    template_name = 'estoque/estoque_form.html'
    success_url = reverse_lazy('estoque:estoque_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProdutoEntradaFormSet(self.request.POST)
        else:
            context['formset'] = ProdutoEntradaFormSet(queryset=ProdutoEntrada.objects.none())  # Cria um queryset vazio para o formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            entrada_estoque = form.save()
            produtos = formset.save(commit=False)

            for produto in produtos:
                produto.entrada = entrada_estoque
                produto.save()
                
                # Se o produto for serializado, salve os IMEIs na tabela EstoqueImei
                if produto.imei:  # Presumindo que o IMEI é obrigatório
                    estoque_imei = EstoqueImei.objects.create(
                        produto=produto.produto,
                        imei=produto.imei,
                        produto_entrada=produto  # Associa o ProdutoEntrada
                    )

            return redirect(self.success_url)
        else:
            return self.form_invalid(form)
        
        
def check_produtos(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    if produto.serializado:
        return JsonResponse({'serializado': True})
    else:
        return JsonResponse({'serializado': False})
    
