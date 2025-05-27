from django.db import models
from vendas.models import Base

class EntradaEstoque(Base):
    fornecedor = models.ForeignKey('estoque.Fornecedor', on_delete=models.PROTECT, related_name='entradas_estoque', verbose_name='Fornecedor')
    data_entrada = models.DateField(verbose_name='Data de Entrada')
    numero_nota = models.CharField(max_length=20, verbose_name='Número da Nota')
    
    @property
    def custo_total(self):
        total = 0
        for produto in self.produtos.all():
            total += produto.custo_total
        return total

    @property
    def venda_total(self):
        total = 0
        for produto in self.produtos.all():
            total += produto.venda_total
        return total
    
    @property
    def quantidade_total(self):
        total = 0
        for produto in self.produtos.all():
            total += produto.quantidade
        return total
    
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
        unique_together = ['imei', 'produto', 'loja']
        verbose_name = 'Estoque IMEI'
        verbose_name_plural = 'Estoques IMEI'


class Estoque(Base):
    produto = models.ForeignKey('produtos.Produto', on_delete=models.CASCADE, related_name='estoque_atual')
    quantidade_disponivel = models.PositiveIntegerField(default=0)

    @property
    def ultima_entrada(self):
        return self.produto.entradas_estoque.last()
    
    def preco_medio(self):
        ultima_entrada = self.produto.entradas_estoque.last()
        if ultima_entrada:
            return f"{ultima_entrada.venda_unitaria:.2f}"
        return 0
    
    def preco_medio_custo(self):
        qtd_entradas = self.produto.entradas_estoque.count()
        total = 0
        for entrada in self.produto.entradas_estoque.all():
            total += entrada.custo_unitario
        
        if qtd_entradas > 0:
            preco_medio = total / qtd_entradas
            preco_formatado = f"{preco_medio:.2f}"
            return preco_formatado
        return 0
    
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
        unique_together = ['loja', 'produto']
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