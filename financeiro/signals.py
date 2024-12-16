from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import GastoFixo, Funcionario, CaixaMensal, CaixaMensalGastoFixo, CaixaMensalFuncionario

@receiver(post_save, sender=GastoFixo)
def associar_gasto_fixo_a_caixas_mensais_abertos(sender, instance, created, **kwargs):
    """Associa um novo Gasto Fixo apenas aos caixas mensais abertos."""
    if created:  # Só executa quando um novo Gasto Fixo é criado
        caixas_mensais_abertos = CaixaMensal.objects.filter(data_fechamento=None)
        for caixa_mensal in caixas_mensais_abertos:
            # Verificar se já existe associação para evitar duplicação
            if not CaixaMensalGastoFixo.objects.filter(caixa_mensal=caixa_mensal, gasto_fixo=instance).exists():
                CaixaMensalGastoFixo.objects.create(
                    caixa_mensal=caixa_mensal,
                    gasto_fixo=instance,
                    valor=0.00,  # Valor padrão
                    observacao=""
                )

@receiver(post_save, sender=Funcionario)
def associar_funcionario_a_caixas_mensais_abertos(sender, instance, created, **kwargs):
    """Associa um novo Funcionário apenas aos caixas mensais abertos."""
    if created:  # Só executa quando um novo Funcionário é criado
        caixas_mensais_abertos = CaixaMensal.objects.filter(data_fechamento=None)
        for caixa_mensal in caixas_mensais_abertos:
            # Verificar se já existe associação para evitar duplicação
            if not CaixaMensalFuncionario.objects.filter(caixa_mensal=caixa_mensal, funcionario=instance).exists():
                CaixaMensalFuncionario.objects.create(
                    caixa_mensal=caixa_mensal,
                    funcionario=instance,
                    salario=0.00,  # Valor padrão
                    comissao=0.00
                )
# ao excluir deve apgar as associações
@receiver(post_delete, sender=GastoFixo)
def desassociar_gasto_fixo_a_caixas_mensais_abertos(sender, instance, **kwargs):
    """Desassocia um Gasto Fixo dos caixas mensais abertos."""
    caixas_mensais_abertos = CaixaMensal.objects.filter(data_fechamento=None)
    for caixa_mensal in caixas_mensais_abertos:
        CaixaMensalGastoFixo.objects.filter(caixa_mensal=caixa_mensal, gasto_fixo=instance).delete()


@receiver(post_delete, sender=Funcionario)
def desassociar_funcionario_a_caixas_mensais_abertos(sender, instance, **kwargs):
    """Desassocia um Funcionário dos caixas mensais abertos."""
    caixas_mensais_abertos = CaixaMensal.objects.filter(data_fechamento=None)
    for caixa_mensal in caixas_mensais_abertos:
        CaixaMensalFuncionario.objects.filter(caixa_mensal=caixa_mensal, funcionario=instance).delete()

