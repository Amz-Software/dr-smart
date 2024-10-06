from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Estoque, EntradaEstoque
from vendas.models import ProdutoVenda

@receiver(post_save, sender=EntradaEstoque)
def atualizar_estoque_entrada(sender, instance, created, **kwargs):
    estoque, _ = Estoque.objects.get_or_create(produto=instance.produto)
    estoque.adicionar_estoque(instance.quantidade)

@receiver(post_delete, sender=EntradaEstoque)
def atualizar_estoque_deletar_entrada(sender, instance, **kwargs):
    estoque = Estoque.objects.get(produto=instance.produto)
    try:
        estoque.remover_estoque(instance.quantidade)
    except ValueError:
        # Caso não consiga remover, você pode lidar com isso aqui (opcional)
        estoque.quantidade_disponivel = 0  # Garante que não fique negativo
        estoque.save()

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
