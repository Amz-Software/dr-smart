from datetime import datetime, timezone
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, ListView
from .models import Caixa
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class IndexView(TemplateView):
    template_name = 'index.html'
    

class CaixaListView(UserPassesTestMixin, ListView):
    model = Caixa
    template_name = 'caixa/caixa_list.html'
    context_object_name = 'caixas'
    
    def test_func(self):
        return self.request.user.has_perm('vendas.view_caixa')
    
    def get_queryset(self):
        query = super().get_queryset()
        data_filter = self.request.GET.get('data_filter')
        if data_filter:
            return query.filter(data_abertura=data_filter)
        
        return query.order_by('-data_abertura')
    
    def post(self, request, *args, **kwargs):
        criar_caixa = request.POST.get('criar_caixa')
        print('Criar caixa:', criar_caixa)  

        if criar_caixa:
            print('Criando caixa')
            today = datetime.now(timezone.utc).date()

            if not Caixa.caixa_aberto(today):
                # Cria o caixa
                Caixa.objects.create(
                    data_abertura=today,
                    criado_por=request.user,
                    modificado_por=request.user,
                    )
                messages.success(request, 'Caixa aberto com sucesso')
                print('Caixa aberto com sucesso')
                return redirect('vendas:caixa_list')
            else:
                messages.warning(request, 'Já existe um caixa aberto para hoje')
                print('Já existe um caixa aberto para hoje')
                return redirect('vendas:caixa_list')
        
        return self.get(request, *args, **kwargs)
