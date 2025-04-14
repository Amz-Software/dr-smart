from django.urls import path
from .models import *
from .views import *


app_name = 'assistencia'

urlpatterns = [
    path('caixas-assistencia/', CaixaAssistenciaListView.as_view(), name='caixa_assistencia_list'),

    path('ordem-servicos/', OrdemServicoListView.as_view(), name='ordem_servico_list'),
    path('ordem-servicos/novo/', OrdemServicoCreateView.as_view(), name='ordem_servico_create'),
    path('ordem-servicos/editar/<int:pk>/', OrdemServicoUpdateView.as_view(), name='ordem_servico_update'),
]
