from django.urls import path
from .models import *
from .views import *


app_name = 'assistencia'

urlpatterns = [
    path('caixas-assistencia/', CaixaAssistenciaListView.as_view(), name='caixa_assistencia_list'),
]
