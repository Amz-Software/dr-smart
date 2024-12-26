from django.urls import path
from .views import *


app_name = 'financeiro'
urlpatterns = [
    path('financeiro/caixa-mensal', CaixaMensalListView.as_view(), name='caixa_mensal_list'),
    path('financeiro/caixa-mensal/novo', caixa_mensal_create , name='caixa_mensal_create'),
    path('financeiro/caixa-mensal/<int:pk>', CaixaMensalDetailView.as_view(), name='caixa_mensal_update'),
    path('financeiro/caixa-mensal/<int:pk>/fechar', fechar_caixa_mensal, name='caixa_mensal_close'),
    path('financeiro/caixa-mensal/<int:pk>/reabrir', reabrir_caixa_mensal, name='caixa_mensal_reopen'),
    path('financeiro/contas-a-receber', ContasAReceberListView.as_view(), name='contas_a_receber_list'),
    path('financeiro/contas-a-receber/<int:pk>', ContasAReceberDetailView.as_view(), name='contas_a_receber_update'),
]