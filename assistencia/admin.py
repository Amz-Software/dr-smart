from django.contrib import admin
from assistencia.models import CaixaAssistencia, OrdemServico, PecaOrdemServico
from .forms import OrdemServicoForm, PecaOrdemServicoForm, pecas_inline_formset

class PecaOrdemServicoInline(admin.TabularInline):
    model = PecaOrdemServico
    extra = 1
    formset = pecas_inline_formset

class OrdemServicoAdmin(admin.ModelAdmin):
    inlines = [PecaOrdemServicoInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        loja = request.session.get('loja_id')
        if loja:
            return qs.filter(loja=loja)
        return qs

# Register your models here.
admin.site.register(CaixaAssistencia)
admin.site.register(OrdemServico, OrdemServicoAdmin)