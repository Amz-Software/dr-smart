from django.urls import path
from .views import CaixaMensalListView, CaixaMensalDetailView, caixa_mensal_create, fechar_caixa_mensal, reabrir_caixa_mensal


app_name = 'financeiro'
urlpatterns = [
    path('financeiro/caixa-mensal', CaixaMensalListView.as_view(), name='caixa_mensal_list'),
    path('financeiro/caixa-mensal/novo', caixa_mensal_create , name='caixa_mensal_create'),
    path('financeiro/caixa-mensal/<int:pk>', CaixaMensalDetailView.as_view(), name='caixa_mensal_update'),
    path('financeiro/caixa-mensal/<int:pk>/fechar', fechar_caixa_mensal, name='caixa_mensal_close'),
    path('financeiro/caixa-mensal/<int:pk>/reabrir', reabrir_caixa_mensal, name='caixa_mensal_reopen'),
]