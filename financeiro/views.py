from django.views.generic import CreateView, UpdateView, ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.forms import inlineformset_factory, modelformset_factory
from django.shortcuts import get_object_or_404
from accounts.views import logout_view
from django.shortcuts import get_object_or_404
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from vendas.views import BaseView
from .models import CaixaMensal, CaixaMensalGastoFixo, CaixaMensalFuncionario, GastosAleatorios
from financeiro.forms import RelatorioSaidaForm
from vendas.models import Loja
from .models import CaixaMensal, CaixaMensalFuncionario, CaixaMensalGastoFixo, GastoFixo, GastosAleatorios
from datetime import datetime, timedelta
from django.db import transaction
from financeiro.forms import *
from vendas.models import Pagamento, Parcela
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required


class CaixaMensalListView(BaseView, PermissionRequiredMixin, ListView):
    model = CaixaMensal
    template_name = 'caixa_mensal/caixa_mensal_list.html'
    context_object_name = 'caixas_mensais'
    paginate_by = 10
    permission_required = 'financeiro.view_caixamensal'
    def get_queryset(self):
        loja_id = self.request.session.get('loja_id')
        loja = Loja.objects.get(id=loja_id)
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            data = search + "-01"
            data = datetime.strptime(data, "%Y-%m-%d").date()
            queryset = queryset.filter(mes__month=data.month, mes__year=data.year, loja=loja).order_by('-mes')
        return queryset.filter(loja=loja).order_by('-mes')


@login_required
@permission_required('financeiro.add_caixamensal', raise_exception=True)
def caixa_mensal_create(request):
    with transaction.atomic():
        
        loja_id = request.session.get('loja_id')
        mes = request.POST.get('mes')

        if mes:
            mes = mes + "-01"
            mes_atual = datetime.strptime(mes, "%Y-%m-%d").date()
        
        if not loja_id:
            messages.error(request, "Loja não selecionada. Selecione uma loja e faça login novamente.")
            return logout_view(request)

        try:
            loja = Loja.objects.get(id=loja_id)
        except Loja.DoesNotExist:
            messages.error(request, "Loja não encontrada. Selecione uma loja e faça login novamente.")
            return logout_view(request)

        if CaixaMensal.objects.filter(loja=loja, mes=mes_atual).exists():
            messages.error(request, "Caixa mensal já criado para este mês.")
            return redirect('financeiro:caixa_mensal_list')

        # Cria o caixa mensal
        caixa_mensal = CaixaMensal.objects.create(
            loja=loja,
            mes=mes_atual,
            valor=0.00,
        )

        # Associar todos os funcionários e gastos fixos
        funcionarios = loja.usuarios.all()
        for funcionario in funcionarios:
            CaixaMensalFuncionario.objects.create(
                caixa_mensal=caixa_mensal,
                funcionario=funcionario,
                salario=0.00,  # Inicializa com valores zero para edição posterior
                comissao=0.00,
            )
        
        gastos_fixos = GastoFixo.objects.filter(loja=loja)
        if gastos_fixos:
            for gasto in gastos_fixos:
                CaixaMensalGastoFixo.objects.create(
                    caixa_mensal=caixa_mensal,
                    gasto_fixo=gasto,
                    valor=0.00,  # Inicializa com valores zero para edição posterior
                    observacao="",
                )
        
        # Redirecionar para a página de detalhes do caixa mensal recém-criado
        messages.success(request, "Caixa mensal criado com sucesso.")
        return redirect('financeiro:caixa_mensal_update', pk=caixa_mensal.pk)

@login_required
@permission_required('financeiro.change_caixamensal', raise_exception=True)
def fechar_caixa_mensal(request, pk):
    caixa_mensal = get_object_or_404(CaixaMensal, pk=pk)
    caixa_mensal.fechar()
    return redirect('financeiro:caixa_mensal_list')

@login_required
@permission_required('financeiro.change_caixamensal', raise_exception=True)
def reabrir_caixa_mensal(request, pk):
    caixa_mensal = get_object_or_404(CaixaMensal, pk=pk)
    caixa_mensal.reabrir()
    return redirect('financeiro:caixa_mensal_list')



# class CaixaMensalCreateView(CreateView):
#     model = CaixaMensal
#     template_name = 'caixa_mensal/caixa_mensal_form.html'
#     fields = ['valor']  # Apenas o campo inicial, loja e mês são automáticos

#     def form_valid(self, form): 
#         form.instance.mes = datetime.now()  # Define o mês atual
#         return super().form_valid(form)


# class CaixaMensalDetailView(DetailView):
#     model = CaixaMensal
#     template_name = 'caixa_mensal/caixa_mensal_form.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         self.object = self.get_object()
#         context['object'] = self.object

#         # Usando Prefetch para carregar os gastos fixos e funcionários relacionados à caixa mensal
#         gastos_fixos_qs = GastoFixo.objects.filter(
#             lojas_gastos_fixos__caixa_mensal=self.object
#         )
#         funcionarios_qs = Funcionario.objects.filter(
#             lojas_funcionarios__caixa_mensal=self.object
#         )

#         # Definindo as consultas para as tabelas intermediárias
#         context['gastos_fixos'] = gastos_fixos_qs
#         context['funcionarios'] = funcionarios_qs

#         # Configurando o formset de Gastos Aleatórios
#         GastosAleatoriosFormSet = inlineformset_factory(
#             CaixaMensal, GastosAleatorios,
#             form=GastosAleatoriosForm,
#             extra=0, can_delete=False
#         )

#         if self.request.method == 'POST':
#             context['gastos_aleatorios_formset'] = GastosAleatoriosFormSet(self.request.POST, instance=self.object)
#         else:
#             context['gastos_aleatorios_formset'] = GastosAleatoriosFormSet(instance=self.object)

#         return context

#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data()

#         # Processando o formulário de Gastos Fixos
#         if 'gastos_fixos_form' in request.POST:
#             for gasto_fixo in self.object.gastos_fixos.all():
#                 valor = request.POST.get(f'valor_{gasto_fixo.id}')
#                 observacao = request.POST.get(f'observacao_{gasto_fixo.id}')
#                 if valor is not None:
#                     gasto_fixo.valor = float(valor) if valor else 0
#                 if observacao is not None:
#                     gasto_fixo.observacao = observacao
#                 gasto_fixo.save()
#             messages.success(request, 'Gastos Fixos atualizados com sucesso.')

#         # Processando o formulário de Funcionários
#         if 'funcionario_form' in request.POST:
#             for funcionario in self.object.funcionarios.all():
#                 salario = request.POST.get(f'salario_{funcionario.id}')
#                 comissao = request.POST.get(f'comissao_{funcionario.id}')
#                 if salario is not None:
#                     funcionario.salario = float(salario) if salario else 0
#                 if comissao is not None:
#                     funcionario.comissao = float(comissao) if comissao else 0
#                 funcionario.save()
#             messages.success(request, 'Funcionários atualizados com sucesso.')

#         # Processando o formset de Gastos Aleatórios
#         gastos_aleatorios_formset = context['gastos_aleatorios_formset']
#         if gastos_aleatorios_formset.is_valid():
#             gastos_aleatorios_formset.save()
#             messages.success(request, 'Gastos Aleatórios atualizados com sucesso.')
#         else:
#             messages.error(request, 'Erro ao atualizar os Gastos Aleatórios.')

#         return HttpResponseRedirect(self.object.get_absolute_url())

class CaixaMensalDetailView(PermissionRequiredMixin, DetailView):
    model = CaixaMensal
    template_name = 'caixa_mensal/caixa_mensal_detail.html'
    context_object_name = 'caixa_mensal'
    permission_required = 'financeiro.view_caixamensal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loja_id = self.request.session.get('loja_id')
        caixa_mensal = self.get_object()
        caixa_mensal_gastos_fixos = CaixaMensalGastoFixo.objects.filter(caixa_mensal=caixa_mensal)
        caixa_mensal_funcionarios = CaixaMensalFuncionario.objects.filter(caixa_mensal=caixa_mensal)
        caixa_mensal_gastos_aleatorios = GastosAleatorios.objects.filter(caixa_mensal=caixa_mensal)

        # Pré-configurar os Gastos Fixos associados ao Caixa Mensal
        self._pre_configurar_gastos_fixos(caixa_mensal)

        # Pré-configurar os Funcionários associados ao Caixa Mensal
        self._pre_configurar_funcionarios(caixa_mensal)

        # Formsets com prefixos
        context['formset_gastos_fixos'] = CaixaMensalGastoFixoFormSet(
            queryset=CaixaMensalGastoFixo.objects.filter(caixa_mensal=caixa_mensal),
            prefix='gastos_fixos'
        )
        context['formset_funcionarios'] = CaixaMensalFuncionarioFormSet(
            queryset=CaixaMensalFuncionario.objects.filter(caixa_mensal=caixa_mensal),
            prefix='funcionarios'
        )
        context['formset_gastos_aleatorios'] = GastosAleatoriosFormSet(
            instance=caixa_mensal,
            prefix='gastos_aleatorios'
        )

        caixas_mes = Caixa.objects.filter(loja_id=loja_id).filter(data_abertura__month=caixa_mensal.mes.month)
        vendas = []

        total_saidas = 0

        for caixa in caixas_mes:
            vendas += caixa.vendas.all()
            total_saidas += caixa.saidas

        total_custo = 0
        total_lucro = 0
        valor_venda_por_tipo_pagamento = {}

        for venda in vendas:
            total_custo += venda.custo_total()
            total_lucro += venda.lucro_total()
            #filtrar pagamentos para o mes atual
            for pagamento in venda.pagamentos.all():
                if not pagamento.tipo_pagamento.nao_contabilizar:
                    if pagamento.tipo_pagamento.nome not in valor_venda_por_tipo_pagamento:
                        valor_venda_por_tipo_pagamento[pagamento.tipo_pagamento.nome] = 0
                    valor_venda_por_tipo_pagamento[pagamento.tipo_pagamento.nome] += pagamento.valor 
        valor_por_tipo_pagamento_total = sum(valor_venda_por_tipo_pagamento.values())

        lucro_total = (valor_por_tipo_pagamento_total - total_custo)

        total_gasto_fixos = sum(gasto.valor for gasto in caixa_mensal_gastos_fixos)
        total_funcionarios = sum(funcionario.salario + funcionario.comissao for funcionario in caixa_mensal_funcionarios)
        total_gastos_aleatorios = sum(gasto.valor for gasto in caixa_mensal_gastos_aleatorios)
        total_gastos = total_gasto_fixos + total_funcionarios + total_gastos_aleatorios

        saldo_final = (caixa_mensal.valor + lucro_total) - total_gastos 

        context = {
            'total_vendas': valor_por_tipo_pagamento_total,
            'valor_venda_por_tipo_pagamento': valor_venda_por_tipo_pagamento.items(),
            'valor_por_tipo_pagamento_total': valor_por_tipo_pagamento_total,
            'total_custo': total_custo,
            'total_lucro': total_lucro,
            'lucro_total': lucro_total,
            'total_saidas': total_gasto_fixos + total_funcionarios + total_gastos_aleatorios,
            'total_gasto_fixos': total_gasto_fixos,
            'total_funcionarios': total_funcionarios,
            'total_gastos_aleatorios': total_gastos_aleatorios,
            'saldo_final': saldo_final,
            'formset_gastos_fixos': context['formset_gastos_fixos'],
            'formset_funcionarios': context['formset_funcionarios'],
            'formset_gastos_aleatorios': context['formset_gastos_aleatorios'],
            'caixa_mensal': caixa_mensal
        }

        return context

    def _pre_configurar_gastos_fixos(self, caixa_mensal):
        """Cria associações de Gastos Fixos ao Caixa Mensal, caso não existam."""
        if not CaixaMensalGastoFixo.objects.filter(caixa_mensal=caixa_mensal).exists():
            gastos_fixos_disponiveis = GastoFixo.objects.all().filter(loja=caixa_mensal.loja)
            for gasto_fixo in gastos_fixos_disponiveis:
                CaixaMensalGastoFixo.objects.create(
                    caixa_mensal=caixa_mensal,
                    gasto_fixo=gasto_fixo,
                    valor=0.00,  # Valor padrão
                    observacao=""
                )

    def _pre_configurar_funcionarios(self, caixa_mensal):
        """Cria associações de Funcionários ao Caixa Mensal, caso não existam."""
        if not CaixaMensalFuncionario.objects.filter(caixa_mensal=caixa_mensal).exists():
            funcionarios_disponiveis = Loja.objects.get(id=self.request.session.get('loja_id')).usuarios.all()
            for funcionario in funcionarios_disponiveis:
                CaixaMensalFuncionario.objects.create(
                    caixa_mensal=caixa_mensal,
                    funcionario=funcionario,
                    salario=0.00,  # Valor padrão
                    comissao=0.00
                )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        caixa_mensal = self.object

        # Inicialização dos formsets com prefixos
        formset_gastos_fixos = CaixaMensalGastoFixoFormSet(
            request.POST,
            queryset=CaixaMensalGastoFixo.objects.filter(caixa_mensal=caixa_mensal),
            prefix='gastos_fixos'
        )
        formset_funcionarios = CaixaMensalFuncionarioFormSet(
            request.POST,
            queryset=CaixaMensalFuncionario.objects.filter(caixa_mensal=caixa_mensal),
            prefix='funcionarios'
        )
        formset_gastos_aleatorios = GastosAleatoriosFormSet(
            request.POST,
            instance=caixa_mensal,
            prefix='gastos_aleatorios'
        )

        # Verificar se os formsets são válidos
        if formset_gastos_fixos.is_valid() and formset_funcionarios.is_valid() and formset_gastos_aleatorios.is_valid():
            # Salvar formset de Gastos Fixos
            instances_gastos_fixos = formset_gastos_fixos.save(commit=False)
            for instance in instances_gastos_fixos:
                instance.caixa_mensal = caixa_mensal
                instance.save()
            formset_gastos_fixos.save_m2m()

            # Salvar formset de Funcionários
            # verificar se o funcionário foi deletado
            for form in formset_funcionarios.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()
            instances_funcionarios = formset_funcionarios.save(commit=False)
            
            for instance in instances_funcionarios:
                instance.caixa_mensal = caixa_mensal
                instance.save()
            formset_funcionarios.save_m2m()

            # Salvar formset de Gastos Aleatórios
            formset_gastos_aleatorios.save()

            # Mensagem de sucesso e redirecionamento
            messages.success(request, "Caixa Mensal atualizado com sucesso!")
            return redirect('financeiro:caixa_mensal_update', pk=caixa_mensal.pk)

        # Caso haja erros, exibir mensagem de erro e retornar o contexto com os formsets
        messages.error(request, "Erro ao atualizar o Caixa Mensal.")
        print(formset_gastos_fixos.errors)
        print(formset_funcionarios.errors)
        print(formset_gastos_aleatorios.errors)
        return self.render_to_response(self.get_context_data(
            formset_gastos_fixos=formset_gastos_fixos,
            formset_funcionarios=formset_funcionarios,
            formset_gastos_aleatorios=formset_gastos_aleatorios
        ))

class ContasAReceberListView(BaseView, PermissionRequiredMixin, ListView):
    model = Pagamento
    template_name = 'contas_a_receber/contas_a_receber_list.html'
    context_object_name = 'contas_a_receber'
    paginate_by = 10
    permission_required = 'vendas.view_pagamento'

    def get_queryset(self):
        loja_id = self.request.session.get('loja_id')
        return Pagamento.objects.order_by('-criado_em').filter(loja_id=loja_id).exclude(tipo_pagamento__caixa=True).filter(tipo_pagamento__parcelas=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        for pagamento in queryset:
            status = self.verificar_atraso_parcela(pagamento)
            pagamento.atrasado = status
        context['contas_a_receber'] = queryset
        return context

    def verificar_atraso_parcela(self, pagamento):
        data_atual = timezone.now().date()
        parcela = pagamento.parcelas_pagamento.filter(pago=False).order_by('data_vencimento').first()
        if parcela and parcela.data_vencimento < data_atual:
            if parcela.valor_restante < parcela.valor:
                return "Pago parcialmente"
            return "Atrasado"
        return "Em dia"
    

class ContasAReceberDetailView(PermissionRequiredMixin, DetailView):
    model = Pagamento
    template_name = 'contas_a_receber/contas_a_receber_detail.html'
    context_object_name = 'conta_a_receber'
    permission_required = 'vendas.view_pagamento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conta_a_receber = self.get_object()
        context['parcela_form'] = ParcelaInlineFormSet(instance=conta_a_receber)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        conta_a_receber = self.object
        parcela_form = ParcelaInlineFormSet(request.POST, instance=conta_a_receber)

        if parcela_form.is_valid():
            parcela_form.save()
            messages.success(request, "Parcelas atualizadas com sucesso!")
            return redirect('financeiro:contas_a_receber_update', pk=conta_a_receber.pk)

        messages.error(request, "Erro ao atualizar as parcelas.")
        return self.render_to_response(self.get_context_data(parcela_form=parcela_form))
    
class RelatorioSaidaView(BaseView, PermissionRequiredMixin, TemplateView):
    template_name = 'relatorio/relatorio_saida.html'
    permission_required = 'financeiro.view_caixamensal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RelatorioSaidaForm()

        return context
    
class FolhaRelatorioSaidaView(BaseView, PermissionRequiredMixin, TemplateView):
    template_name = 'relatorio/folha_relatorio_saida.html'
    permission_required = 'financeiro.view_caixamensal'

    def get_context_data(self, **kwargs):
        data_inicio = self.request.GET.get('data_inicial')
        data_fim = self.request.GET.get('data_final')
        lojas = self.request.GET.getlist('lojas')
        saidas = []

        if data_inicio and data_fim:
            lojas = Loja.objects.filter(id__in=lojas)
            data_final = datetime.strptime(data_fim, "%Y-%m-%d").date() + timedelta(days=1)

            for loja in lojas:
                caixas = Caixa.objects.filter(loja=loja).filter(data_abertura__range=[data_inicio, data_final]).filter(data_fechamento__isnull=False)
                for caixa in caixas:
                    saidas += caixa.lancamentos_caixa.filter(tipo_lancamento='2')

        context = super().get_context_data(**kwargs)
        context['saidas'] = saidas
        # retornar apenas os nomes das lojas
        context['lojas'] = lojas.values_list('nome', flat=True)
        context['data_inicio'] = datetime.strptime(data_inicio, "%Y-%m-%d").date() if data_inicio else None
        context['data_fim'] = datetime.strptime(data_fim, "%Y-%m-%d").date() if data_fim else None
        context['total_saida'] = sum(saida.valor for saida in saidas)
        context['quantidade_saida'] = len(saidas)

        return context