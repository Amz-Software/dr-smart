from django.contrib import admin
from django.urls import path

from utils.gerador_views import generate_views
from vendas.forms import *
from vendas.models import *
from .views import *

tipoPagamentoViews = generate_views(TipoPagamento, TipoPagamentoForm, 10, template_dir='tipopagamento')
tipoEntregaViews = generate_views(TipoEntrega, TipoEntregaForm, 10, template_dir='tipoentrega')
tipoVendaViews = generate_views(TipoVenda, TipoVendaForm, 10, template_dir='tipovenda')

app_name = 'vendas'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    #caixa
    path('caixas/', CaixaListView.as_view(), name='caixa_list'),
    path('caixas/<int:pk>/', CaixaDetailView.as_view(), name='caixa_detail'),
    path('caixa/caixa-total/', CaixaTotalView.as_view(), name='caixa_total'),

    #cliente
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('clientes/editar/', cliente_editar_view, name='cliente_edit_form'),
    
    #tipo de pagamento
    path('tipopagamento/', tipoPagamentoViews['list_view'].as_view(), name='tipos_pagamento'),
    path('tipos-pagamento/novo/', tipoPagamentoViews['create_view'].as_view(), name='tipopagamento_create'),
    path('tipos-pagamento/detalhe/<int:pk>/', tipoPagamentoViews['detail_view'].as_view(), name='tipopagamento_detail'),
    path('tipos-pagamento/editar/<int:pk>/', tipoPagamentoViews['update_view'].as_view(), name='tipopagamento_update'),

    #tipo de entrega
    path('tipoentrega/', tipoEntregaViews['list_view'].as_view(), name='tipos_entrega'),
    path('tipos-entrega/novo/', tipoEntregaViews['create_view'].as_view(), name='tipoentrega_create'),
    path('tipos-entrega/detalhe/<int:pk>/', tipoEntregaViews['detail_view'].as_view(), name='tipoentrega_detail'),
    path('tipos-entrega/editar/<int:pk>/', tipoEntregaViews['update_view'].as_view(), name='tipoentrega_update'),

    #tipo de venda
    path('tipovenda/', tipoVendaViews['list_view'].as_view(), name='tipos_venda'),
    path('tipos-venda/novo/', tipoVendaViews['create_view'].as_view(), name='tipovenda_create'),
    path('tipos-venda/detalhe/<int:pk>/', tipoVendaViews['detail_view'].as_view(), name='tipovenda_detail'),
    path('tipos-venda/editar/<int:pk>/', tipoVendaViews['update_view'].as_view(), name='tipovenda_update'),

    #venda
    path('vendas/', VendaListView.as_view(), name='venda_list'),
    path('vendas/nova/', VendaCreateView.as_view(), name='venda_create'),
]
