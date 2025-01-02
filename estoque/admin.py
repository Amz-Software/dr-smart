from django.contrib import admin
from .models import *
# Register your models here.


class AdminBase(admin.ModelAdmin):
    list_display = ('loja', 'criado_em', 'modificado_em', 'criado_por', 'modificado_por')
    readonly_fields = ('criado_em', 'modificado_em', 'criado_por', 'modificado_por')
    
    def save_model(self, request, obj, form, change):
        obj.save(user=request.user) 
        super().save_model(request, obj, form, change)


@admin.register(EntradaEstoque)
class EntradaEstoqueAdmin(AdminBase):
  pass


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
  

@admin.register(ProdutoEntrada)
class ProdutoEntradaAdmin(AdminBase):
  list_display = ('entrada', 'produto', 'imei', 'custo_unitario', 'venda_unitaria', 'quantidade', 'custo_total', 'venda_total') + AdminBase.list_display
  search_fields = ('produto__nome', 'imei')
  list_filter = ('entrada', 'produto')
  
@admin.register(EstoqueImei)
class EstoqueImeiAdmin(AdminBase):
  list_display = ('produto', 'imei', 'vendido') + AdminBase.list_display
  search_fields = ('produto__nome', 'imei')
  list_filter = ('produto', 'vendido')
  