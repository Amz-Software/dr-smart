from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from assistencia.models import CaixaAssistencia, OrdemServico
from produtos.models import Produto
from vendas.models import Loja
from django.views import View
from .forms import OrdemServicoForm, pecas_inline_formset, PecaOrdemServicoForm
from .models import CaixaAssistencia
from estoque.models import Estoque
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

class CaixaAssistenciaListView(BaseView, PermissionRequiredMixin, ListView):
    model = CaixaAssistencia
    template_name = 'caixa-assistencia/caixa_assistencia_list.html'
    context_object_name = 'caixas'
    permission_required = 'assistencia.view_assistencia'
    
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

            if not CaixaAssistencia.caixa_aberto(today, Loja.objects.get(id=request.session.get('loja_id'))):
                CaixaAssistencia.objects.create(
                    data_abertura=today,
                    criado_por=request.user,
                    modificado_por=request.user,
                    loja=Loja.objects.get(id=request.session.get('loja_id'))
                    )
                messages.success(request, 'Caixa aberto com sucesso')
                return redirect('assistencia:caixa_assistencia_list')
            else:
                messages.warning(request, 'Já existe um caixa aberto para hoje')
                return redirect('assistencia:caixa_assistencia_list')
            
        
        fechar_caixa = request.POST.get('fechar_caixa')
        if fechar_caixa:
            today = timezone.localtime(timezone.now()).date()
            try:
                caixa = CaixaAssistencia.objects.get(id=fechar_caixa, loja=request.session.get('loja_id'))
                caixa.data_fechamento = today
                caixa.save(user=request.user)
                messages.success(request, 'Caixa fechado com sucesso')
                return redirect('assistencia:caixa_assistencia_list')
            except:
                messages.warning(request, 'Não existe caixa aberto para hoje')
                return redirect('assistencia:caixa_assistencia_list')
        
        return self.get(request, *args, **kwargs)

class OrdemServicoListView(BaseView, PermissionRequiredMixin, ListView):
    model = OrdemServico
    template_name = 'ordem-servico/ordem_servico_list.html'
    context_object_name = 'ordens_servico'
    permission_required = 'assistencia.view_ordemservico'
    
class OrdemServicoCreateView(BaseView, PermissionRequiredMixin, CreateView):
    model = OrdemServico
    form_class = OrdemServicoForm
    template_name = 'ordem-servico/ordem_servico_create.html'
    permission_required = 'assistencia.add_ordemservico'
    success_url = reverse_lazy('assistencia:ordem_servico_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loja = self.get_loja()

        context['pecas_formset'] = pecas_inline_formset(self.request.POST or None, form_kwargs={'loja': loja})

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        loja = self.get_loja()
        if loja:
            kwargs['loja'] = loja
        return kwargs

    def form_valid(self, form):
        # verificar se existe caixa aberto
        context = self.get_context_data()
        formset = context['pecas_formset']
        loja = self.get_loja()
        caixa = CaixaAssistencia.caixa_aberto(timezone.localtime(timezone.now()).date(), self.get_loja())

        if not (formset.is_valid() and form.is_valid()):
            messages.error(self.request, 'Erro ao salvar as peças')
            return self.form_invalid(form)

        if not caixa:
            messages.error(self.request, 'Não existe caixa aberto para hoje')
            return self.form_invalid(form)
        
        try:
            with transaction.atomic():
                self._salvar_os(form, loja)
                self._salvar_pecas(formset, loja)
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Erro ao salvar: {str(e)}')
            return self.form_invalid(form)

    def _salvar_os(self, form, loja):
        form.instance.loja = loja
        form.instance.criado_por = self.request.user
        form.instance.modificado_por = self.request.user
        form.instance.caixa = CaixaAssistencia.caixa_aberto(timezone.localtime(timezone.now()).date(), loja)
        self.object = form.save()

    def _salvar_pecas(self, formset, loja):
        for form in formset.save(commit=False):
            peca = form.produto
            quantidade = form.quantidade
            valor_unitario = form.valor_unitario
            self._validar_estoque(peca, quantidade, loja)
            self._atualizar_estoque(peca, quantidade, loja)
            form.ordem_servico = self.object
            form.produto = peca
            form.valor_unitario = valor_unitario
            form.loja = loja
            form.criado_por = self.request.user
            form.modificado_por = self.request.user
            form.save()

    def _validar_estoque(self, peca, quantidade, loja):
        estoque = Estoque.objects.filter(produto=peca, loja=loja).first()
        if not estoque or estoque.quantidade_disponivel < quantidade:
            raise ValueError(f"Quantidade indisponível para o produto {peca.nome}")

    def _atualizar_estoque(self, peca, quantidade, loja):
        estoque = Estoque.objects.filter(produto=peca, loja=loja).first()
        if estoque:
            estoque.quantidade_disponivel -= quantidade
            estoque.save()

class OrdemServicoUpdateView(BaseView, PermissionRequiredMixin, UpdateView):
    model = OrdemServico
    form_class = OrdemServicoForm
    template_name = 'ordem-servico/ordem_servico_update.html'
    permission_required = 'assistencia.change_ordemservico'
    success_url = reverse_lazy('assistencia:ordem_servico_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loja = self.get_loja()

        context['pecas_formset'] = pecas_inline_formset(self.request.POST or None, instance=self.object, form_kwargs={'loja': loja})

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        loja = self.get_loja()
        if loja:
            kwargs['loja'] = loja
        return kwargs

    def form_valid(self, form):
        form.instance.modificado_por = self.request.user
        return super().form_valid(form)
