from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView
# from estoque.forms import EntradaForm
from estoque.models import EntradaEstoque, Estoque, EstoqueImei, ProdutoEntrada
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from produtos.models import Produto
from vendas.models import Loja
from .forms import EntradaEstoqueForm, EstoqueImeiForm, ProdutoEntradaForm, ProdutoEntradaFormSet, ProdutoEntradaEditFormSet
from vendas.views import BaseView
from vendas.models import Venda

class EstoqueListView(BaseView, PermissionRequiredMixin, ListView):
    model = Estoque
    template_name = 'estoque/estoque_list.html'
    context_object_name = 'produtos'
    permission_required = 'estoque.view_estoque'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loja_id = self.request.session.get('loja_id')
        context['loja_id'] = loja_id
        return context
    
    def get_queryset(self):
        loja_id = self.request.session.get('loja_id')
        loja = get_object_or_404(Loja, pk=loja_id)
        query = super().get_queryset().filter(produto__loja=loja)
        search = self.request.GET.get('search', None)
        if search:
            query = query.filter(produto__nome__icontains=search).filter(produto__loja=loja)
            
        return query

class EntradaListView(BaseView, PermissionRequiredMixin, ListView):
    model = EntradaEstoque
    template_name = 'estoque/estoque_entrada_list.html'
    context_object_name = 'entradas'
    permission_required = 'estoque.view_entradaestoque'
    paginate_by = 10
    
    def get_queryset(self):
        query = super().get_queryset()
        loja_id = self.request.session.get('loja_id')
        loja = get_object_or_404(Loja, pk=loja_id)
        search = self.request.GET.get('search', None)
        if search:
            query = query.filter(fornecedor__nome__icontains=search).filter(loja=loja)
            
        return query.order_by('-data_entrada').filter(loja=loja)
    
class EntradaDetailView(PermissionRequiredMixin, DetailView):
    model = EntradaEstoque
    template_name = 'estoque/estoque_entrada_detail.html'
    context_object_name = 'entrada'
    permission_required = 'estoque.view_entradaestoque'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produtos'] = ProdutoEntrada.objects.filter(entrada=self.object)
        return context
    
class EntradaUpdateView(PermissionRequiredMixin, UpdateView):
    # levar em consideração que pode ter uma venda e diminuir o estoque
    model = EntradaEstoque
    form_class = EntradaEstoqueForm
    template_name = 'estoque/estoque_form_edit.html'
    success_url = reverse_lazy('estoque:estoque_list')
    permission_required = 'estoque.change_entradaestoque'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loja_id = self.request.session.get('loja_id')
        if self.request.POST:
            context['formset'] = ProdutoEntradaEditFormSet(self.request.POST, form_kwargs={'loja': loja_id})
        else:
            context['formset'] = ProdutoEntradaEditFormSet(queryset=ProdutoEntrada.objects.filter(entrada=self.object), form_kwargs={'loja': loja_id})
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        loja_id = self.request.session.get('loja_id')
        loja = get_object_or_404(Loja, pk=loja_id)
        if form.is_valid() and formset.is_valid():
            entrada_estoque = form.save(commit=False)
            entrada_estoque.loja = loja
            produtos = formset.save(commit=False)
            # verificar se excluiu algum produto
            for produto in formset.deleted_objects:
                produto.delete()

            for produto in produtos:
                produto.entrada = entrada_estoque
                produto.loja = loja
                produto.save(user=self.request.user)
                
                # Se o produto for serializado, salve os IMEIs na tabela EstoqueImei
                if produto.imei:  # Presumindo que o IMEI é obrigatório
                    estoque_imei = EstoqueImei.objects.create(
                        produto=produto.produto,
                        imei=produto.imei,
                        produto_entrada=produto,
                        loja=loja
                    )
                    estoque_imei.save(user=self.request.user)

            #verificar se a entrada não esta vazia
            if not entrada_estoque.produtos.all():
                entrada_estoque.delete()
                messages.error(self.request, 'Entrada Excluída, pois não possui produtos.')
                return redirect(self.success_url)

            entrada_estoque.save(user=self.request.user)
            messages.success(self.request, 'Entrada de estoque atualizada com sucesso!')
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

class AdicionarEntradaEstoqueView(PermissionRequiredMixin, CreateView):
    model = EntradaEstoque
    form_class = EntradaEstoqueForm
    template_name = 'estoque/estoque_form.html'
    success_url = reverse_lazy('estoque:estoque_list')
    permission_required = 'estoque.add_entradaestoque'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loja_id = self.request.session.get('loja_id')
        if self.request.POST:
            context['formset'] = ProdutoEntradaFormSet(self.request.POST, form_kwargs={'loja': loja_id})
        else:
            context['formset'] = ProdutoEntradaFormSet(queryset=ProdutoEntrada.objects.none(), form_kwargs={'loja': loja_id})  # Cria um queryset vazio para o formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        loja_id = self.request.session.get('loja_id')
        loja = get_object_or_404(Loja, pk=loja_id)
        if form.is_valid() and formset.is_valid():
            entrada_estoque = form.save(commit=False)
            entrada_estoque.loja = loja
            entrada_estoque.save(user=self.request.user)
            produtos = formset.save(commit=False)

            for produto in produtos:
                produto.entrada = entrada_estoque
                produto.loja = loja
                produto.save(user=self.request.user)
                
                # Se o produto for serializado, salve os IMEIs na tabela EstoqueImei
                if produto.imei:  # Presumindo que o IMEI é obrigatório
                    estoque_imei = EstoqueImei.objects.create(
                        produto=produto.produto,
                        imei=produto.imei,
                        produto_entrada=produto,
                        loja=loja
                    )
                    estoque_imei.save(user=self.request.user)
            
            messages.success(self.request, 'Entrada de estoque criada com sucesso!')
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)
        

class EstoqueImeiListView(BaseView, PermissionRequiredMixin, ListView):
    model = EstoqueImei
    template_name = 'estoque/estoque_imei_list.html'
    context_object_name = 'produtos'
    permission_required = 'estoque.view_estoqueimei'
    paginate_by = 10
    
    def get_queryset(self):
        loja_id = self.request.session.get('loja_id')
        loja = get_object_or_404(Loja, pk=loja_id)
        query = super().get_queryset().filter(produto__loja=loja)
        
        search = self.request.GET.get('search', None)
        if search:
            query = query.filter(Q(imei__icontains=search)|Q(produto__nome__icontains=search)).filter(produto__loja=loja)
            
        return query
    

class EstoqueImeiUpdateView(PermissionRequiredMixin, UpdateView):
    model = EstoqueImei
    form_class = EstoqueImeiForm
    template_name = 'estoque/estoque_imei_form.html'
    success_url = reverse_lazy('estoque:estoque_imei_list')
    permission_required = 'estoque.change_estoqueimei'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['produtoentrada_formset'] = ProdutoEntradaFormSet(self.request.POST, queryset=ProdutoEntrada.objects.filter(entrada=self.object.produto_entrada.entrada))
        else:
            data['produtoentrada_formset'] = ProdutoEntradaFormSet(queryset=ProdutoEntrada.objects.filter(entrada=self.object.produto_entrada.entrada))
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        produtoentrada_formset = context['produtoentrada_formset']
        if form.is_valid() and produtoentrada_formset.is_valid():
            self.object = form.save()
            produtoentrada_formset.save()
            messages.success(self.request, 'Estoque IMEI e Produto Entrada atualizados com sucesso!')
            return redirect(self.success_url)
        else:
            messages.error(self.request, 'Erro ao atualizar Estoque IMEI ou Produto Entrada')
            return self.form_invalid(form)

@login_required
def check_produtos(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    if produto.tipo.numero_serial:
        return JsonResponse({'serializado': True})
    else:
        return JsonResponse({'serializado': False})
    
    
class EstoqueImeiSearchView(View):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        produto_id = request.GET.get('produto_id', None)
        loja_id = self.request.session.get('loja_id')
        loja = get_object_or_404(Loja, pk=loja_id)
        queryset = EstoqueImei.objects.filter(vendido=False).filter(
            Q(imei__icontains=term) | Q(produto__nome__icontains=term)
        ).filter(produto__loja=loja)
        if produto_id:
            queryset = queryset.filter(produto_id=produto_id)
        
        results = []
        for imei in queryset:
            results.append({
                'id': imei.id,
                'text': f'{imei.imei} - {imei.produto.nome}'
            })
        return JsonResponse({'results': results})
    
def inventario_estoque_pdf (request):
    loja = get_object_or_404(Loja, pk=request.session.get('loja_id'))
    produtos = Estoque.objects.filter(loja=loja).filter(quantidade_disponivel__gt=0)
    
    context = {
        'produtos': produtos,
        'loja': loja
    }

    return render(request, "estoque/folha_estoque.html", context)