from django.contrib import admin
from django.urls import path
from .views import ProdutoListView, ProdutoCreateView, ProdutoUpdateView, ProdutoDeleteView, ProdutoDetailView

app_name = 'produtos'
urlpatterns = [
    path('produtos/', ProdutoListView.as_view(), name='produtos'),
    path('produtos/novo/', ProdutoCreateView.as_view(), name='produto_create'),
    path('produtos/detalhe/<int:pk>/', ProdutoDetailView.as_view(), name='produto_detail'),
    path('produtos/editar/<int:pk>/', ProdutoUpdateView.as_view(), name='produto_update'),
    path('produtos/deletar/<int:pk>/', ProdutoDeleteView.as_view(), name='produto_delete'),
]
