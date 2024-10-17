from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, ListView, DetailView
from .models import Caixa
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone


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
        
        return query.order_by('-criado_em')
    
    def post(self, request, *args, **kwargs):
        criar_caixa = request.POST.get('criar_caixa')

        if criar_caixa:
            today = timezone.localtime(timezone.now()).date()

            if not Caixa.caixa_aberto(today):
                Caixa.objects.create(
                    data_abertura=today,
                    criado_por=request.user,
                    modificado_por=request.user,
                    )
                messages.success(request, 'Caixa aberto com sucesso')
                return redirect('vendas:caixa_list')
            else:
                messages.warning(request, 'Já existe um caixa aberto para hoje')
                return redirect('vendas:caixa_list')
            
        
        fechar_caixa = request.POST.get('fechar_caixa')
        if fechar_caixa:
            today = timezone.localtime(timezone.now()).date()
            try:
                caixa = Caixa.objects.get(id=fechar_caixa)
                caixa.data_fechamento = today
                caixa.save(user=request.user)
                messages.success(request, 'Caixa fechado com sucesso')
                return redirect('vendas:caixa_list')
            except:
                messages.warning(request, 'Não existe caixa aberto para hoje')
                return redirect('vendas:caixa_list')
        
        return self.get(request, *args, **kwargs)


class CaixaDetailView(UserPassesTestMixin, DetailView):
    model = Caixa
    template_name = 'caixa/caixa_detail.html'
    
    def test_func(self):
        return self.request.user.has_perm('vendas.view_caixa')
    