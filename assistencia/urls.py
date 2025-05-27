from django.urls import path
from .models import *
from .views import *


app_name = 'assistencia'

urlpatterns = [
    path('assistencia/caixas-assistencia/', CaixaAssistenciaListView.as_view(), name='caixa_assistencia_list'),
    path('assistencia/caixas-assistencia/<int:pk>/', CaixaAssistenciaDetailView.as_view(), name='caixa_assistencia_detail'),

    path('assistencia/ordem-servicos/', OrdemServicoListView.as_view(), name='ordem_servico_list'),
    path('assistencia/ordem-servicos/novo/', OrdemServicoCreateView.as_view(), name='ordem_servico_create'),
    path('assistencia/ordem-servicos/editar/<int:pk>/', OrdemServicoUpdateView.as_view(), name='ordem_servico_update'),

    path('assistencia/contas-a-receber-assistencia/', ContasReceberAssistenciaListView.as_view(), name='contas_a_receber_list'),
    path('assistencia/contas-a-receber-assistencia/<int:pk>/', ContasReceberAssistenciaDetailView.as_view(), name='contas_a_receber_detail'),
]
