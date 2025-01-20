from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Estoque, EntradaEstoque, ProdutoEntrada, EstoqueImei
from vendas.models import ProdutoVenda, Venda

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

@receiver(pre_save, sender=ProdutoEntrada)
def salvar_quantidade_antiga(instance, **kwargs):
    if instance.pk:
        instance._quantidade_antiga = ProdutoEntrada.objects.get(pk=instance.pk).quantidade
    else:
        instance._quantidade_antiga = 0


@receiver(post_save, sender=ProdutoEntrada)
def atualizar_estoque_entrada(instance, created, **kwargs):
    if created:
        # Verifica se o estoque já existe para o produto e loja
        estoque = Estoque.objects.filter(produto=instance.produto, loja=instance.loja).first()
        if not estoque:
            estoque = Estoque.objects.create(produto=instance.produto, loja=instance.loja)
        estoque.adicionar_estoque(instance.quantidade)
    else:
        estoque = Estoque.objects.filter(produto=instance.produto, loja=instance.loja).first()
        quantidade_antiga = instance._quantidade_antiga
        quantidade_nova = instance.quantidade
        
        if quantidade_nova > quantidade_antiga:
            estoque.adicionar_estoque(quantidade_nova - quantidade_antiga)
        elif quantidade_nova < quantidade_antiga:
            estoque.remover_estoque(quantidade_antiga - quantidade_nova)



# @receiver(post_delete, sender=EntradaEstoque)
# def atualizar_estoque_deletar_entrada(sender, instance, **kwargs):
#     estoque = Estoque.objects.get(produto=instance.produto)
#     try:
#         estoque.remover_estoque(instance.quantidade)
#     except ValueError:
#         estoque.quantidade_disponivel = 0
#         estoque.save()


# # ATUALIZAR ESTOQUE APÓS VENDA
# @receiver(post_save, sender=ProdutoVenda)
# def atualizar_estoque_venda(sender, instance, created, **kwargs):
#     if created:
#         print('Pos - signal', instance)
#         print('Pos - signal', instance.produto)
#         print('Pos - signal', instance.loja)
#         estoque = Estoque.objects.filter(produto=instance.produto, loja=instance.loja).first()
#         print(estoque)
#         try:
#             estoque.remover_estoque(instance.quantidade)
#         except ValueError:
#             raise ValidationError(f"Estoque insuficiente para o produto {instance.produto.nome}.")

@receiver(post_delete, sender=ProdutoVenda)
def atualizar_estoque_deletar_venda(sender, instance, **kwargs):
    estoque = Estoque.objects.filter(produto=instance.produto, loja=instance.loja).first()
    estoque.adicionar_estoque(instance.quantidade)

@receiver(post_save, sender=Venda)
def atualizar_estoque_apos_cancelar_venda(sender, instance, **kwargs):
    """
    Atualiza o estoque quando uma venda é cancelada (is_deleted=True).
    """
    if instance.is_deleted:  # Apenas processa se a venda foi cancelada
        # Recupera todos os itens da venda
        venda_items = ProdutoVenda.objects.filter(venda=instance)

        for item in venda_items:
            # Atualiza o estoque do IMEI, se existir
            if item.imei:
                estoque_imei = EstoqueImei.objects.filter(imei=item.imei).first()
                if estoque_imei:  # Apenas processa se encontrar algo
                    estoque_imei.vendido = False
                    estoque_imei.save()
                else:
                    raise Exception(f"Estoque IMEI não encontrado para o IMEI {item.imei}.")

            # Atualiza o estoque geral do produto
            try:
                estoque = Estoque.objects.get(produto=item.produto, loja=item.loja)
                estoque.adicionar_estoque(item.quantidade)
                estoque.save()
            except Estoque.DoesNotExist:
                raise Exception(f"Estoque não encontrado para o produto {item.produto.nome} na loja {item.loja}.")