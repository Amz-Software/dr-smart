from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pagamento, Parcela
from datetime import timedelta

@receiver(post_save, sender=Pagamento)
def criar_ou_atualizar_parcelas(sender, instance, created, **kwargs):
    if created: 
        for numero in range(1, instance.parcelas + 1):
            Parcela.objects.create(
                pagamento=instance,
                numero_parcela=numero,
                valor=instance.valor_parcela,
                data_vencimento=calcular_data_vencimento(instance.data_primeira_parcela, numero)
            )
    else:  
        Parcela.objects.filter(pagamento=instance).delete()

        for numero in range(1, instance.parcelas + 1):
            Parcela.objects.create(
                pagamento=instance,
                numero_parcela=numero,
                valor=instance.valor_parcela,
                data_vencimento=calcular_data_vencimento(instance.data_primeira_parcela, numero)
            )

def calcular_data_vencimento(data_primeira_parcela, numero_parcela):
    return data_primeira_parcela + timedelta(days=30 * (numero_parcela - 1))
