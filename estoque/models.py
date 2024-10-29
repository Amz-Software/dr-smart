from django.db import models
from vendas.models import Base

class EntradaEstoque(Base):
    fornecedor = models.ForeignKey('estoque.Fornecedor', on_delete=models.PROTECT, related_name='entradas_estoque', verbose_name='Fornecedor')
    data_entrada = models.DateField(verbose_name='Data de Entrada')
    numero_nota = models.CharField(max_length=20, verbose_name='Número da Nota')
    

    def __str__(self):
        return f"Entrada {self.numero_nota} - {self.fornecedor.nome}"

    class Meta:
        verbose_name = 'Entrada de Estoque'
        verbose_name_plural = 'Entradas de Estoque'

class ProdutoEntrada(Base):
    entrada = models.ForeignKey(EntradaEstoque, on_delete=models.CASCADE, related_name='produtos', verbose_name='Entrada de Estoque')
    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT, related_name='entradas_estoque', verbose_name='Produto')
    imei = models.CharField(max_length=20, blank=True, null=True, verbose_name='IMEI')
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Custo Unitário')
    venda_unitaria = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Venda Unitária')
    quantidade = models.PositiveIntegerField(verbose_name='Quantidade', default=1)

    @property
    def custo_total(self):
        return self.custo_unitario * self.quantidade
    
    @property
    def venda_total(self):
        return self.venda_unitaria * self.quantidade

    def __str__(self):
        return f"{self.produto.nome} - Quantidade: {self.quantidade}"

    class Meta:
        verbose_name = 'Produto na Entrada de Estoque'
        verbose_name_plural = 'Produtos na Entrada de Estoque'
        

class EstoqueImei(Base):
    produto = models.ForeignKey('produtos.Produto', on_delete=models.CASCADE, related_name='estoque_imei')
    imei = models.CharField(max_length=20, verbose_name='IMEI')
    vendido = models.BooleanField(default=False, verbose_name='Vendido')
    produto_entrada = models.ForeignKey(ProdutoEntrada, on_delete=models.CASCADE, related_name='estoque_imei', blank=True, null=True)
    
    def __str__(self):
        return self.imei
    
    class Meta:
        verbose_name = 'Estoque IMEI'
        verbose_name_plural = 'Estoques IMEI'


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
        ordering = ['quantidade_disponivel']


class Fornecedor(Base):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Fornecedores'