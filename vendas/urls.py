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
    path('caixa/lancamento/<int:pk>/', lancamento_delete_view, name='lancamento_delete'),
    path('caixa/caixa-total/lancamento/<int:pk>/', lancamento_total_delete_view, name='caixa_total_lancamento_delete'),

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
    path('vendas/editar/<int:pk>/', VendaUpdateView.as_view(), name='venda_update'),
    path('vendas/nova/', VendaCreateView.as_view(), name='venda_create'),
    path('vendas/detail/<int:pk>/', VendaDetailView.as_view(), name='venda_detail'),
    path('vendas/cancelar/<int:id>/', cancelar_venda , name='venda_cancel'),
    
    #Loja
    path('lojas/', LojaListView.as_view(), name='loja_list'),
    path('lojas/nova/', LojaCreateView.as_view(), name='loja_create'),
    path('lojas/editar/<int:pk>/', LojaUpdateView.as_view(), name='loja_update'),
    path('lojas/detalhe/<int:pk>/', LojaDetailView.as_view(), name='loja_detail'),
    
    
    path('info-products/', product_information, name='info_produto'),
    path('info-payment/', get_payment_method , name='payment_data'),
    
    path('select2/fields/auto.json', ProdutoAutoComplete.as_view(), name='produto-autocomplete'),
    path('produtos/ajax/', get_produtos, name='produtos_ajax'),

    path('vendas/nota/<int:pk>/', VendaPDFView.as_view(), name='venda_pdf'),
    path('caixa/folha/<int:pk>/', FolhaCaixaPDFView.as_view(), name='caixa_pdf'),
    path('caixa/folha-produtos/<int:pk>/', FolhaProdutoPDFView.as_view(), name='caixa_produto_pdf'),
    path('gerar-carne/<int:pk>/<str:tipo>/', folha_carne_view, name='gerar_carne'),
    path('venda/contrato/<int:pk>/', contrato_view, name='gerar_contrato'),
    
    path('vendas/relatorio/', RelatorioVendasView.as_view(), name='venda_relatorio'),
    path('vendas/relatorio/folha/', FolhaRelatorioVendasView.as_view(), name='folha_venda_relatorio'),
    path('prdutos-vendidos/', ProdutoVendidoListView.as_view(), name='produto_vendido_list'),
]
