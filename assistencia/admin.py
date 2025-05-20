from django.contrib import admin
from assistencia.models import CaixaAssistencia, OrdemServico, PecaOrdemServico, PagamentoAssistencia, ParcelaAssistencia
from .forms import (
    OrdemServicoForm, PecaOrdemServicoForm, pecas_inline_formset,
    PagamentoAssistenciaForm, FormaPagamentoAssistenciaFormSet,
)

class PecaOrdemServicoInline(admin.TabularInline):
    model = PecaOrdemServico
    extra = 1
    formset = pecas_inline_formset

class PagamentoAssistenciaInline(admin.TabularInline):
    model = PagamentoAssistencia
    extra = 1

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.criado_por = request.user
        obj.modificado_por = request.user
        super().save_model(request, obj, form, change)

class OrdemServicoAdmin(admin.ModelAdmin):
    inlines = [PecaOrdemServicoInline, PagamentoAssistenciaInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        loja = request.session.get('loja_id')
        if loja:
            return qs.filter(loja=loja)
        return qs

# Register your models here.
admin.site.register(CaixaAssistencia)
admin.site.register(OrdemServico, OrdemServicoAdmin)
admin.site.register(PecaOrdemServico)
admin.site.register(PagamentoAssistencia)
admin.site.register(ParcelaAssistencia)