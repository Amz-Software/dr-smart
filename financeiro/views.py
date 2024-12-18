from django.views.generic import CreateView, UpdateView, ListView, DetailView
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
from django.views.generic import DetailView
from .models import CaixaMensal, CaixaMensalGastoFixo, CaixaMensalFuncionario, GastosAleatorios
from financeiro.forms import GastosAleatoriosForm
from vendas.models import Loja
from .models import CaixaMensal, CaixaMensalFuncionario, CaixaMensalGastoFixo, Funcionario, GastoFixo, GastosAleatorios
from datetime import datetime
from django.db import transaction
from financeiro.forms import *


class CaixaMensalListView(ListView):
    model = CaixaMensal
    template_name = 'caixa_mensal/caixa_mensal_list.html'
    context_object_name = 'caixas_mensais'

    # def get_queryset(self):
    #     return CaixaMensal.objects.filter(loja__user=self.request.user)


@transaction.atomic
@login_required
def caixa_mensal_create(request):
    loja_id = request.session.get('loja_id')
    
    if not loja_id:
        messages.error(request, "Loja não selecionada. Selecione uma loja e faça login novamente.")
        return logout_view(request)

    try:
        loja = Loja.objects.get(id=loja_id)
    except Loja.DoesNotExist:
        messages.error(request, "Loja não encontrada. Selecione uma loja e faça login novamente.")
        return logout_view(request)

    mes_atual = timezone.now().date().replace(day=1)

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
    funcionarios = Funcionario.objects.filter(user__lojas=loja)
    for funcionario in funcionarios:
        CaixaMensalFuncionario.objects.create(
            caixa_mensal=caixa_mensal,
            funcionario=funcionario,
            salario=0.00,  # Inicializa com valores zero para edição posterior
            comissao=0.00,
        )
    
    gastos_fixos = GastoFixo.objects.all()
    for gasto in gastos_fixos:
        CaixaMensalGastoFixo.objects.create(
            caixa_mensal=caixa_mensal,
            gasto_fixo=gasto,
            valor=0.00,  # Inicializa com valores zero para edição posterior
            observacao="",
        )
    
    # Redirecionar para a página de detalhes do caixa mensal recém-criado
    messages.success(request, "Caixa mensal criado com sucesso.")
    return redirect('financeiro:caixa_mensal_detail', pk=caixa_mensal.pk)


def fechar_caixa_mensal(request, pk):
    caixa_mensal = get_object_or_404(CaixaMensal, pk=pk)
    caixa_mensal.fechar()
    return redirect('financeiro:caixa_mensal_list')

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

class CaixaMensalDetailView(DetailView):
    model = CaixaMensal
    template_name = 'caixa_mensal/caixa_mensal_detail.html'
    context_object_name = 'caixa_mensal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        caixa_mensal = self.get_object()

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

        return context

    def _pre_configurar_gastos_fixos(self, caixa_mensal):
        """Cria associações de Gastos Fixos ao Caixa Mensal, caso não existam."""
        if not CaixaMensalGastoFixo.objects.filter(caixa_mensal=caixa_mensal).exists():
            gastos_fixos_disponiveis = GastoFixo.objects.all()
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
            funcionarios_disponiveis = Funcionario.objects.all()
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

        print(request.POST)

        # Verificar se os formsets são válidos
        if formset_gastos_fixos.is_valid() and formset_funcionarios.is_valid() and formset_gastos_aleatorios.is_valid():
            # Salvar formset de Gastos Fixos
            instances_gastos_fixos = formset_gastos_fixos.save(commit=False)
            for instance in instances_gastos_fixos:
                instance.caixa_mensal = caixa_mensal
                instance.save()
            formset_gastos_fixos.save_m2m()

            # Salvar formset de Funcionários
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




