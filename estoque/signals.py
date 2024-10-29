from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Estoque, EntradaEstoque, ProdutoEntrada
from vendas.models import ProdutoVenda

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
        estoque, _ = Estoque.objects.get_or_create(produto=instance.produto)
        estoque.adicionar_estoque(instance.quantidade)
    else:
        estoque = Estoque.objects.get(produto=instance.produto)
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


# ATUALIZAR ESTOQUE APÓS VENDA
@receiver(post_save, sender=ProdutoVenda)
def atualizar_estoque_venda(sender, instance, created, **kwargs):
    if created:
        estoque = Estoque.objects.get(produto=instance.produto)
        try:
            estoque.remover_estoque(instance.quantidade)
        except ValueError:
            raise ValidationError(f"Estoque insuficiente para o produto {instance.produto.nome}.")

@receiver(post_delete, sender=ProdutoVenda)
def atualizar_estoque_deletar_venda(sender, instance, **kwargs):
    estoque = Estoque.objects.get(produto=instance.produto)
    estoque.adicionar_estoque(instance.quantidade)
