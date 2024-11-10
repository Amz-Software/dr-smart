from django.urls import path
from .views import *


app_name = 'estoque'
urlpatterns = [
    path('estoque/', EstoqueListView.as_view(), name='estoque_list'),
    path('estoque/entrada/criar', AdicionarEntradaEstoqueView.as_view() , name='estoque_entrada'),
    path('estoque/entrada/', EntradaListView.as_view(), name='entrada_list'),
    path('estoque/entrada/<int:pk>/', EntradaDetailView.as_view(), name='entrada_detail'),
    
    path('estoque_imei/', EstoqueImeiListView.as_view(), name='estoque_imei_list'),
    path('estoque_imei/editar/<int:pk>/', EstoqueImeiUpdateView.as_view(), name='estoque_imei_update'),
    
    #api
    path('produto/details/<int:produto_id>/', check_produtos, name='produto_details'),
]