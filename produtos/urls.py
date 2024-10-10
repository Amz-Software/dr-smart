from django.contrib import admin
from django.urls import path
from .views import ProdutoListView


app_name = 'produtos'
urlpatterns = [
    path('produtos/', ProdutoListView.as_view(), name='produtos'),
]
