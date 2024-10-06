from django.db import models
from vendas.models import Base

class EntradaEstoque(Base):
    fornecedor = models.ForeignKey('estoque.Fornecedor', on_delete=models.PROTECT, related_name='entradas_estoque')
    data_entrada = models.DateField()
    numero_nota = models.CharField(max_length=20)
    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT, related_name='entradas_estoque')
    imei = models.CharField(max_length=20, blank=True, null=True)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    venda_unitaria = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField()
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    venda_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"Nota {self.numero_nota} - {self.produto.nome}"
    
    def save(self, *args, **kwargs):
        self.custo_total = self.custo_unitario * self.quantidade
        self.venda_total = self.venda_unitaria * self.quantidade
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Entradas de Estoque'


class Estoque(Base):
    produto = models.OneToOneField('produtos.Produto', on_delete=models.CASCADE, related_name='estoque_atual')
    quantidade_disponivel = models.PositiveIntegerField(default=0)
    
    def adicionar_estoque(self, quantidade):
        self.quantidade_disponivel += quantidade
        self.save()
        
    def remover_estoque(self, quantidade):
        if self.quantidade_disponivel >= quantidade:
            self.quantidade_disponivel -= quantidade
            self.save()
        else:
            raise ValueError("Estoque insuficiente.")

    
    def __str__(self):
        return f"Estoque de {self.produto.nome}: {self.quantidade_disponivel}"
    
    class Meta:
        verbose_name_plural = 'Estoques'


class Fornecedor(Base):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Fornecedores'