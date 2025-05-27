from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.utils import timezone
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from assistencia.models import CaixaAssistencia, OrdemServico, PagamentoAssistencia
from produtos.models import Produto
from vendas.models import Loja
from django.views import View
from .forms import (
    OrdemServicoForm, pecas_inline_formset,
    FormaPagamentoAssistenciaFormSet, FormaPagamentoAssistenciaEditFormSet, parcela_inline_formset
)
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
        
        return query.order_by('-criado_em').filter(loja=self.get_loja())
    
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

class CaixaAssistenciaDetailView(BaseView, PermissionRequiredMixin, DetailView):
    model = CaixaAssistencia
    template_name = 'caixa-assistencia/caixa_assistencia_detail.html'
    permission_required = 'assistencia.view_caixaassistencia'
    context_object_name='caixa'
    
    def get_context_data(self, **kwargs):
        loja_id = self.request.session.get('loja_id')
        loja = get_object_or_404(Loja, id=loja_id)
        context = super().get_context_data(**kwargs)
        context['ordens_servico'] = OrdemServico.objects.filter(
            loja=loja,
            caixa=self.object
        ).order_by('-criado_em')
        return context

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

        context['pecas_formset'] = pecas_inline_formset(
            self.request.POST or None,
            form_kwargs={'loja': loja}
        )
        context['pagamento_formset'] = FormaPagamentoAssistenciaFormSet(
            self.request.POST or None,
            form_kwargs={'loja': loja}
        )

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        loja = self.get_loja()
        if loja:
            kwargs['loja'] = loja
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        pecas_formset = context['pecas_formset']
        pagamento_formset = context['pagamento_formset']
        loja = self.get_loja()
        caixa_aberto = CaixaAssistencia.caixa_aberto(
            timezone.localtime(timezone.now()).date(), loja
        )

        if not (pecas_formset.is_valid() and pagamento_formset.is_valid() and form.is_valid()):
            messages.error(self.request, 'Erro ao salvar as peças ou pagamentos')
            return self.form_invalid(form)

        if not caixa_aberto:
            messages.error(self.request, 'Não existe caixa aberto para hoje')
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                self._salvar_os(form, loja)
                self._salvar_pecas(pecas_formset, loja)
                self._processar_pagamentos(pagamento_formset, loja)
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Erro ao salvar: {str(e)}')
            return self.form_invalid(form)

    def _salvar_os(self, form, loja):
        form.instance.loja = loja
        form.instance.criado_por = self.request.user
        form.instance.modificado_por = self.request.user
        form.instance.caixa = CaixaAssistencia.objects.get(
            loja=loja,
            data_abertura=timezone.localtime(timezone.now()).date(),
            data_fechamento__isnull=True
        )
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

    def _processar_pagamentos(self, formset, loja):
        """Processa pagamentos do formset para ordem de serviço."""
        for pagamento in formset.save(commit=False):
            pagamento.ordem_servico = self.object
            pagamento.loja = loja
            pagamento.save()

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
    
    def get_success_url(self):
        return reverse_lazy('assistencia:ordem_servico_update', kwargs={'pk': self.object.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        loja = self.get_loja()
        if loja:
            kwargs['loja'] = loja
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loja = self.get_loja()
        self.request.session['ordem_servico_id'] = self.object.id  # Guarda o ID da OS na sessão

        if self.request.POST:
            context['pecas_formset'] = pecas_inline_formset(
                self.request.POST,
                instance=self.object,
                form_kwargs={'loja': loja}
            )
            context['pagamento_formset'] = FormaPagamentoAssistenciaEditFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'loja': loja}
            )
        else:
            context['pecas_formset'] = pecas_inline_formset(
                instance=self.object,
                form_kwargs={'loja': loja}
            )
            context['pagamento_formset'] = FormaPagamentoAssistenciaEditFormSet(
                instance=self.object,
                form_kwargs={'loja': loja}
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        pecas_formset = context['pecas_formset']
        pagamento_formset = context['pagamento_formset']
        loja = self.get_loja()

        if not (form.is_valid() and pecas_formset.is_valid() and pagamento_formset.is_valid()):
            messages.error(self.request, 'Erro ao salvar as peças ou pagamentos')
            print(pecas_formset.errors)
            print(pagamento_formset.errors)
            return self.form_invalid(form)
        
        try:
            with transaction.atomic():
                self._atualizar_os(form, loja)
                self._processar_pecas(pecas_formset, loja)
                self._processar_pagamentos(pagamento_formset, loja)
                messages.success(self.request, 'Ordem de serviço atualizada com sucesso')
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Erro ao atualizar: {str(e)}')
            return self.form_invalid(form)
        
    def _atualizar_os(self, form, loja):
        """Salva a instância da ordem de serviço com possíveis alterações."""
        form.instance.loja = loja
        form.instance.modificado_por = self.request.user
        form.instance.caixa = CaixaAssistencia.objects.get(
            loja=loja,
            data_abertura=timezone.localtime(timezone.now()).date(),
            data_fechamento__isnull=True
        )
        self.object = form.save()
        
    def _processar_pecas(self, formset, loja):
        """Cria/atualiza/remove peças, validando e atualizando estoques."""
        pecas_modificadas = formset.save(commit=False)
        
        # Deletar peças marcadas para exclusão
        for deletada in formset.deleted_objects:
            self._restaurar_estoque(deletada.produto, deletada.quantidade, loja)
            deletada.delete()
            
        # Salvar/atualizar peças (novas ou já existentes)
        for peca in pecas_modificadas:
            produto = peca.produto
            quantidade = peca.quantidade
            
            self._validar_estoque(produto, quantidade, loja)
            self._atualizar_estoque(produto, quantidade, loja)
            
            peca.ordem_servico = self.object
            peca.loja = loja
            peca.modificado_por = self.request.user
            if not peca.pk:  # Se for uma nova peça
                peca.criado_por = self.request.user
            peca.save()
            
        formset.save_m2m()

    def _processar_pagamentos(self, formset, loja):
        """Processa pagamentos do formset, incluindo exclusão e criação/atualização."""
        pagamentos_modificados = formset.save(commit=False)
        
        # Remover pagamentos excluídos
        for deletado in formset.deleted_objects:
            deletado.delete()
            
        # Salvar/atualizar pagamentos
        for pagamento in pagamentos_modificados:
            pagamento.ordem_servico = self.object
            pagamento.loja = loja
            pagamento.save()
            
        formset.save_m2m()

    def _validar_estoque(self, peca, quantidade, loja):
        estoque = Estoque.objects.filter(produto=peca, loja=loja).first()
        if not estoque or estoque.quantidade_disponivel < quantidade:
            raise ValueError(f"Quantidade indisponível para o produto {peca.nome}")

    def _atualizar_estoque(self, peca, quantidade, loja):
        estoque = Estoque.objects.filter(produto=peca, loja=loja).first()
        if estoque:
            estoque.quantidade_disponivel -= quantidade
            estoque.save()
            
    def _restaurar_estoque(self, produto, quantidade, loja):
        """Restaura a quantidade do estoque se o item for removido."""
        estoque = Estoque.objects.filter(produto=produto, loja=loja).first()
        if estoque:
            estoque.quantidade_disponivel += quantidade
            estoque.save()

class ContasReceberAssistenciaListView(BaseView, PermissionRequiredMixin, ListView):
    model = PagamentoAssistencia
    template_name = 'contas-receber-assistencia/contas_a_receber_list.html'
    context_object_name = 'contas_receber'
    permission_required = 'assistencia.view_pagamentoassistencia'

    def get_queryset(self):
        loja_id = self.request.session.get('loja_id')
        return PagamentoAssistencia.objects.order_by('-criado_em').filter(loja_id=loja_id).exclude(tipo_pagamento__caixa=True).filter(tipo_pagamento__parcelas=True)
    
class ContasReceberAssistenciaDetailView(BaseView, PermissionRequiredMixin, DetailView):
    model = PagamentoAssistencia
    template_name = 'contas-receber-assistencia/contas_a_receber_detail.html'
    context_object_name = 'conta_a_receber'
    permission_required = 'assistencia.view_pagamentoassistencia'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conta_receber = self.get_object()
        print(conta_receber.parcelas_pagamento_assistencia.all())
        context['parcela_form'] = parcela_inline_formset(instance=conta_receber)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        conta_receber = self.object
        parcela_form = parcela_inline_formset(request.POST, instance=conta_receber)

        if parcela_form.is_valid():
            parcela_form.save()
            messages.success(request, "Parcelas atualizadas com sucesso!")
            return redirect('assistencia:contas_a_receber_detail', pk=conta_receber.pk)

        messages.error(request, "Erro ao atualizar as parcelas.")
        return self.render_to_response(self.get_context_data(parcela_form=parcela_form))