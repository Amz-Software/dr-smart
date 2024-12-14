from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.forms import inlineformset_factory, modelformset_factory
from django.shortcuts import get_object_or_404
from accounts.views import logout_view

from financeiro.forms import GastosAleatoriosForm
from vendas.models import Loja
from .models import CaixaMensal, CaixaMensalFuncionario, CaixaMensalGastoFixo, Funcionario, GastoFixo, GastosAleatorios
from datetime import datetime
from django.db import transaction


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
    
    # Formulário para gastos variáveis (inline)
    GastosAleatoriosFormSet = modelformset_factory(
        GastosAleatorios, fields=('descricao', 'valor', 'observacao'), extra=1
    )
    if request.method == "POST":
        formset = GastosAleatoriosFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('financeiro:caixa_mensal_list')
    else:
        formset = GastosAleatoriosFormSet(queryset=GastosAleatorios.objects.none())

    return render(request, 'caixa_mensal/caixa_mensal_form.html', {
        'caixa_mensal': caixa_mensal,
        'formset': formset,
    })


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


from django.shortcuts import get_object_or_404
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView
from .models import CaixaMensal, CaixaMensalGastoFixo, CaixaMensalFuncionario, GastosAleatorios

class CaixaMensalDetailView(DetailView):
    model = CaixaMensal
    template_name = 'caixa_mensal/caixa_mensal_detail.html'
    context_object_name = 'caixa_mensal'

    def get_object(self, queryset=None):
        """Recupera o objeto CaixaMensal"""
        return get_object_or_404(CaixaMensal, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """Adiciona formulários ao contexto da view"""
        caixa_mensal = self.object  # Garantir que o objeto está disponível

        context = super().get_context_data(**kwargs)  # Contexto básico
        
        context['caixa_mensal'] = caixa_mensal
        
        # Formulários para gasto fixo e funcionário
        CaixaMensalGastoFixoFormSet = modelformset_factory(
            CaixaMensalGastoFixo, fields=('gasto_fixo', 'valor', 'observacao'), extra=0
        )
        context['formset_gastos_fixos'] = CaixaMensalGastoFixoFormSet(
            queryset=CaixaMensalGastoFixo.objects.filter(caixa_mensal=caixa_mensal)
        )

        CaixaMensalFuncionarioFormSet = modelformset_factory(
            CaixaMensalFuncionario, fields=('funcionario', 'salario', 'comissao'), extra=0
        )
        context['formset_funcionarios'] = CaixaMensalFuncionarioFormSet(
            queryset=CaixaMensalFuncionario.objects.filter(caixa_mensal=caixa_mensal)
        )

        GastosAleatoriosFormSet = modelformset_factory(
            GastosAleatorios, fields=('descricao', 'valor', 'observacao'), extra=1
        )
        context['formset_gastos_aleatorios'] = GastosAleatoriosFormSet(
            queryset=GastosAleatorios.objects.filter(caixa_mensal=caixa_mensal)
        )

        return context


    def get(self, request, *args, **kwargs):
        """Sobrescreve o método get para definir self.object"""
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Lida com o envio dos formulários de gasto fixo, funcionário e gasto aleatório"""
        self.object = self.get_object()
        caixa_mensal = self.object

        # Processar os formulários de gasto fixo
        CaixaMensalGastoFixoFormSet = modelformset_factory(
            CaixaMensalGastoFixo, fields=('gasto_fixo', 'valor', 'observacao'), extra=0
        )
        formset_gastos_fixos = CaixaMensalGastoFixoFormSet(request.POST)
        
        # Processar os formulários de funcionário
        CaixaMensalFuncionarioFormSet = modelformset_factory(
            CaixaMensalFuncionario, fields=('funcionario', 'salario', 'comissao'), extra=0
        )
        formset_funcionarios = CaixaMensalFuncionarioFormSet(request.POST)
        
        # Processar os formulários de gastos aleatórios
        GastosAleatoriosFormSet = modelformset_factory(
            GastosAleatorios, fields=('descricao', 'valor', 'observacao'), extra=1
        )
        formset_gastos_aleatorios = GastosAleatoriosFormSet(request.POST)

        # Verificar se todos os formulários são válidos
        if formset_gastos_fixos.is_valid() and formset_funcionarios.is_valid() and formset_gastos_aleatorios.is_valid():
            formset_gastos_fixos.save()
            formset_funcionarios.save()
            formset_gastos_aleatorios.save()

            # Redireciona após sucesso
            return HttpResponseRedirect(reverse('financeiro:caixa_mensal_detail', kwargs={'pk': caixa_mensal.pk}))

        # Caso contrário, renderiza novamente com os formulários inválidos
        context = self.get_context_data()
        context['formset_gastos_fixos'] = formset_gastos_fixos
        context['formset_funcionarios'] = formset_funcionarios
        context['formset_gastos_aleatorios'] = formset_gastos_aleatorios
        return self.render_to_response(context)