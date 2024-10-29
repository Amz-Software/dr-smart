from django.urls import path
from .views import *


app_name = 'estoque'
urlpatterns = [
    path('estoque/', EstoqueListView.as_view(), name='estoque_list'),
    path('estoque/entrada/', AdicionarEntradaEstoqueView.as_view() , name='estoque_entrada'),
    path('estoque/entrada/', EntradaListView.as_view(), name='entrada_list'),
    
    #api
    path('produto/details/<int:produto_id>/', check_produtos, name='produto_details'),
]