from django.urls import path
from .views import EstoqueCreateView, EstoqueListView


app_name = 'estoque'
urlpatterns = [
    path('estoque/', EstoqueListView.as_view(), name='estoque_list'),
    path('estoque/entrada/', EstoqueCreateView.as_view(), name='estoque_entrada'),
]