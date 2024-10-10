from django.contrib import admin
from django.urls import path
from .views import *


app_name = 'vendas'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('caixas/', CaixaListView.as_view(), name='caixa_list'),
]
