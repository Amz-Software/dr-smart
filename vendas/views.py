from datetime import datetime
from typing import Any
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, DeleteView, UpdateView, View
from django.utils.timezone import localtime, now
from estoque.models import Estoque, EstoqueImei
from produtos.models import Produto
from vendas.forms import ClienteForm, ComprovantesClienteForm, ContatoAdicionalForm, LojaForm, VendaForm, ProdutoVendaFormSet, FormaPagamentoFormSet
from .models import Caixa, Cliente, Loja, Pagamento, ProdutoVenda, Venda
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils import timezone
from django.db import transaction


class BaseView(View):
    def get_loja(self):
        loja_id = self.request.session.get('loja_id')
        if loja_id:
            return get_object_or_404(Loja, id=loja_id)
        return None

    def get_queryset(self):
        loja = self.get_loja()
        if loja:
            return super().get_queryset().filter(loja=loja)
        
        if not loja:
            raise Http404("Loja não encontrada para o usuário.")

        return super().get_queryset()


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    

class CaixaListView(BaseView, PermissionRequiredMixin, ListView):
    model = Caixa
    template_name = 'caixa/caixa_list.html'
    context_object_name = 'caixas'
    permission_required = 'vendas.view_caixa'
    
    def get_queryset(self):
        query = super().get_queryset()
        data_filter = self.request.GET.get('search')
        if data_filter:
            return query.filter(data_abertura=data_filter)
        
        return query.order_by('-criado_em')
    
    def post(self, request, *args, **kwargs):
        criar_caixa = request.POST.get('criar_caixa')

        if criar_caixa:
            today = timezone.localtime(timezone.now()).date()

            if not Caixa.caixa_aberto(today):
                Caixa.objects.create(
                    data_abertura=today,
                    criado_por=request.user,
                    modificado_por=request.user,
                    loja=Loja.objects.get(id=request.session.get('loja_id'))
                    )
                messages.success(request, 'Caixa aberto com sucesso')
                return redirect('vendas:caixa_list')
            else:
                messages.warning(request, 'Já existe um caixa aberto para hoje')
                return redirect('vendas:caixa_list')
            
        
        fechar_caixa = request.POST.get('fechar_caixa')
        if fechar_caixa:
            today = timezone.localtime(timezone.now()).date()
            try:
                caixa = Caixa.objects.get(id=fechar_caixa, loja=request.session.get('loja_id'))
                caixa.data_fechamento = today
                caixa.save(user=request.user)
                messages.success(request, 'Caixa fechado com sucesso')
                return redirect('vendas:caixa_list')
            except:
                messages.warning(request, 'Não existe caixa aberto para hoje')
                return redirect('vendas:caixa_list')
        
        return self.get(request, *args, **kwargs)


class CaixaDetailView(PermissionRequiredMixin, DetailView):
    model = Caixa
    template_name = 'caixa/caixa_detail.html'
    permission_required = 'vendas.view_caixa'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendas'] = self.object.vendas.filter(is_deleted=False)
        return context
    

class ClienteListView(BaseView, PermissionRequiredMixin, ListView):
    model = Cliente
    template_name = 'cliente/cliente_list.html'
    context_object_name = 'items'
    paginate_by = 10
    permission_required = 'vendas.view_cliente'
    
    def get_queryset(self):
        query = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            return query.filter(nome__icontains=search)
        
        return query.order_by('nome')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form_cliente'] = ClienteForm()
        context['form_adicional'] = ContatoAdicionalForm() 
        context['form_comprovantes'] = ComprovantesClienteForm()
        return context
    
    def post(self, request, *args, **kwargs):
        cliente_id = request.POST.get('cliente_id')  # Verifique se há um cliente_id
        
        if cliente_id:  # Se cliente_id existe, é uma edição
            cliente = Cliente.objects.get(id=cliente_id)
            form_cliente = ClienteForm(request.POST, instance=cliente)
            
            # Usamos as instâncias existentes de contato e comprovantes para evitar duplicação
            form_adicional = ContatoAdicionalForm(request.POST, instance=cliente.contato_adicional)
            form_comprovantes = ComprovantesClienteForm(request.POST, request.FILES, instance=cliente.comprovantes)
        else:  # Se não, é um novo cadastro
            form_cliente = ClienteForm(request.POST)
            form_adicional = ContatoAdicionalForm(request.POST)
            form_comprovantes = ComprovantesClienteForm(request.POST, request.FILES)
        
        if form_cliente.is_valid() and form_adicional.is_valid() and form_comprovantes.is_valid():
            cliente = form_cliente.save(commit=False)
            endereco = form_adicional.save(commit=False)  # Salve o contato sem commit para associá-lo
            comprovantes = form_comprovantes.save(commit=False)  # Salve comprovantes sem commit
            
            # Associa as instâncias e depois salva tudo
            cliente.contato_adicional = endereco
            cliente.comprovantes = comprovantes
            
            endereco.save()  # Salva as instâncias associadas
            comprovantes.save()
            cliente.save()

            # Mensagem de sucesso baseada em ação de edição ou criação
            if cliente_id:
                messages.success(request, 'Cliente atualizado com sucesso')
            else:
                messages.success(request, 'Cliente cadastrado com sucesso')
                    
            return redirect('vendas:cliente_list')
        
        # Mensagem de erro e retorno do formulário em caso de falha na validação
        messages.error(request, 'Erro ao cadastrar cliente')
        return self.get(request, *args, **kwargs)


def cliente_editar_view(request):
    cliente_id = request.GET.get('cliente_id')
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    form_cliente = ClienteForm(instance=cliente)
    form_adicional = ContatoAdicionalForm(instance=cliente.contato_adicional)
    form_comprovantes = ComprovantesClienteForm(instance=cliente.comprovantes)
    
    return render(request, 'cliente/form_cliente.html', {
        'form_cliente': form_cliente,
        'form_adicional': form_adicional,
        'form_comprovantes': form_comprovantes,
        'cliente_id': cliente_id,
    })

class VendaListView(BaseView, PermissionRequiredMixin, ListView):
    model = Venda
    template_name = 'venda/venda_list.html'
    context_object_name = 'vendas'
    paginate_by = 10
    permission_required = 'vendas.view_venda'
    
    def get_queryset(self):
        query = super().get_queryset()
        data_filter = self.request.GET.get('search')
        if data_filter:
            return query.filter(data_venda=data_filter)
        
        return query.order_by('-criado_em')

class VendaCreateView(PermissionRequiredMixin, CreateView):
    model = Venda
    form_class = VendaForm
    template_name = 'venda/venda_create.html'
    success_url = reverse_lazy('vendas:venda_list')
    permission_required = 'vendas.add_venda'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['produto_venda_formset'] = ProdutoVendaFormSet(self.request.POST)
            context['pagamento_formset'] = FormaPagamentoFormSet(self.request.POST)
        else:
            context['produto_venda_formset'] = ProdutoVendaFormSet()
            context['pagamento_formset'] = FormaPagamentoFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        produto_venda_formset = context['produto_venda_formset']
        pagamento_formset = context['pagamento_formset']
        
        if produto_venda_formset.is_valid() and pagamento_formset.is_valid() and form.is_valid():
            is_caixa_aberto = Caixa.caixa_aberto(localtime(now()).date())

            if not is_caixa_aberto:
                messages.warning(self.request, 'Não é possível realizar vendas com o caixa fechado')
                return self.form_invalid(form)
            
            # Iniciar uma transação atômica
            try:
                with transaction.atomic():
                    form.instance.criado_por = self.request.user
                    form.instance.modificado_por = self.request.user
                    form.instance.caixa = Caixa.objects.get(data_abertura=localtime(now()).date())
                    form.instance.data_venda = localtime(now())
                    self.object = form.save()

                    # Salvar produtos da venda
                    produto_venda_formset.instance = self.object

                    for produto_venda in produto_venda_formset:
                        produto = produto_venda.cleaned_data.get('produto')
                        quantidade = produto_venda.cleaned_data.get('quantidade')
                        imei = produto_venda.cleaned_data.get('imei')

                        loja = self.request.session.get('loja_id')
                        produto = Produto.objects.select_related('estoque_atual').get(id=produto.id)

                        if quantidade > produto.estoque_atual.quantidade_disponivel:
                            messages.warning(self.request, f'Quantidade de {produto} indisponível')
                            raise ValueError(f'Quantidade indisponível para {produto}')  # Forçar rollback
                        
                        if produto.tipo.numero_serial:    
                            try:
                                produto_imei = EstoqueImei.objects.get(imei=imei, produto=produto)
                                if produto_imei.vendido:
                                    messages.warning(self.request, f'IMEI {imei} já vendido')
                                    raise ValueError(f'IMEI {imei} já vendido')  # Forçar rollback
                                produto_imei.vendido = True
                                produto_imei.save()
                            except EstoqueImei.DoesNotExist:
                                messages.warning(self.request, f'IMEI {imei} não encontrado')
                                raise ValueError(f'IMEI {imei} não encontrado')  # Forçar rollback

                        # Atualizar o estoque
                        self.atualizar_estoque(produto, quantidade, loja)
                    
                    produto_venda_formset.save()

                    # Salvar pagamentos
                    pagamento_formset.instance = self.object
                    pagamento_formset.save()

                return super().form_valid(form)

            except Exception as e:
                # Garantir rollback e exibir erro genérico
                messages.error(self.request, f"Erro ao processar a venda: {str(e)}")
                return self.form_invalid(form)
        
        return self.form_invalid(form)

    def atualizar_estoque(self, produto, quantidade, loja_id):
        try:
            loja = get_object_or_404(Loja, id=loja_id)
            estoque = Estoque.objects.get(produto=produto, loja=loja)
            if quantidade > estoque.quantidade_disponivel:
                raise ValueError(f'Estoque insuficiente para o produto {produto.nome}')
            estoque.remover_estoque(quantidade)
            estoque.save()
        except Estoque.DoesNotExist:
            raise ValueError(f'Estoque não encontrado para o produto {produto.nome} na loja {loja.nome}')


class VendaDetailView(PermissionRequiredMixin, DetailView):
    model = Venda
    template_name = 'venda/venda_detail.html'
    permission_required = 'vendas.view_venda'
    

def cancelar_venda(request, id):
    venda = get_object_or_404(Venda, id=id)
    if venda.is_deleted:
        messages.warning(request, 'Venda já cancelada')
        return redirect('vendas:venda_list')
    
    if not Caixa.caixa_aberto(localtime(now()).date()):
        messages.warning(request, 'Não é possível cancelar vendas com o caixa fechado')
        return redirect('vendas:venda_list')
    
    venda.is_deleted = True
    venda.save()
    messages.success(request, 'Venda cancelada com sucesso')
    return redirect('vendas:venda_list')
    
class CaixaTotalView(PermissionRequiredMixin, TemplateView):
    template_name = 'caixa/caixa_total.html'
    permission_required = 'vendas.view_caixa'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['caixas'] = Caixa.objects.all()
        
        return context
    

class LojaListView(BaseView, PermissionRequiredMixin, ListView):
    model = Loja
    template_name = 'loja/loja_list.html'
    context_object_name = 'lojas'
    permission_required = 'vendas.view_loja'
    
    def get_queryset(self):
        query = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            return query.filter(nome__icontains=search)
        
        return query.order_by('nome')

class LojaCreateView(PermissionRequiredMixin, CreateView):
    model = Loja
    form_class = LojaForm
    template_name = 'loja/loja_form.html'
    permission_required = 'vendas.add_loja'
    
    def form_valid(self, form):
        messages.success(self.request, 'Loja cadastrada com sucesso')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('vendas:loja_detail', kwargs={'pk': self.object.id})
    

class LojaUpdateView(PermissionRequiredMixin, UpdateView):
    model = Loja
    form_class = LojaForm
    template_name = 'loja/loja_form.html'
    permission_required = 'vendas.change_loja'
    
    def form_valid(self, form):
        messages.success(self.request, 'Loja atualizada com sucesso')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('vendas:loja_detail', kwargs={'pk': self.object.id})

    
class LojaDetailView(PermissionRequiredMixin, DetailView):
    model = Loja
    template_name = 'loja/loja_detail.html'
    permission_required = 'vendas.view_loja'
    

def product_information(request):
    product_id = request.GET.get('product_id')
    imei = request.GET.get('imei')
    product = get_object_or_404(Produto, id=product_id)
    if imei:    
        try:
            product_imei = EstoqueImei.objects.get(imei=imei, produto=product)
            if product_imei.vendido:
                return JsonResponse({'status': 'error', 'message': 'IMEI já vendido'}, status=400)
            else:
                return JsonResponse({'status': 'success', 'product': product.nome, 'price': product.estoque_atual.preco_medio()})
        except EstoqueImei.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'IMEI não encontrado'}, status=404)
    else:
        return JsonResponse({'status': 'success', 'product': product.nome, 'price': product.estoque_atual.preco_medio()})
    

def get_payment_method(request):
    payment_id = request.GET.get('payment_id')
    payment = get_object_or_404(Pagamento, id=payment_id)
    
    if payment:
        return JsonResponse({
            'status': 'success',
            'parcela': payment.tipo_pagamento.parcelas,
            'financeira': payment.tipo_pagamento.financeira,
            'caixa': payment.tipo_pagamento.caixa
        })



