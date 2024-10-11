from django.contrib import admin
from .models import *
# Register your models here.


class AdminBase(admin.ModelAdmin):
    list_display = ('criado_em', 'modificado_em')
    readonly_fields = ('criado_em', 'modificado_em')
    
    def save_model(self, request, obj, form, change):
        obj.save(user=request.user) 
        super().save_model(request, obj, form, change)


@admin.register(EntradaEstoque)
class EntradaEstoqueAdmin(AdminBase):
  list_display = ('quantidade','fornecedor', 'data_entrada', 'numero_nota', 'produto', 'imei', 'custo_unitario', 'venda_unitaria', 'quantidade', 'custo_total', 'venda_total') + AdminBase.list_display
  search_fields = ('numero_nota', 'produto__nome', 'fornecedor__nome')
  list_filter = ('data_entrada', 'fornecedor', 'produto')


@admin.register(Estoque)
class EstoqueAdmin(AdminBase):
  list_display = ('produto', 'quantidade_disponivel') + AdminBase.list_display
  search_fields = ('produto__nome',)
  list_filter = ('produto',)


@admin.register(Fornecedor)
class FornecedorAdmin(AdminBase):
  list_display = ('nome', 'telefone', 'email') + AdminBase.list_display
  search_fields = ('nome', 'telefone', 'email')
  list_filter = ('nome',)