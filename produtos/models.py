from django.db import models
from vendas.models import Base

class Produto(Base):
    codigo = models.CharField(max_length=20)
    nome = models.CharField(max_length=100)
    tipo = models.ForeignKey('produtos.TipoProduto', on_delete=models.PROTECT, related_name='produtos_tipo')
    fabricante = models.ForeignKey('produtos.Fabricante', on_delete=models.PROTECT, related_name='produtos_fabricante')
    cor = models.ForeignKey('produtos.CorProduto', on_delete=models.PROTECT, related_name='produtos_cor')
    memoria = models.ForeignKey('produtos.MemoriaProduto', on_delete=models.PROTECT, related_name='produtos_memoria')
    estado = models.ForeignKey('produtos.EstadoProduto', on_delete=models.PROTECT, related_name='produtos_estado')
    
    @property
    def total_vendas(self):
        return self.produto_vendas.count()
    
    def __str__(self):
        return f"{self.nome} ({self.codigo})"


class TipoProduto(Base):
    nome = models.CharField(max_length=100)
    numero_serial = models.BooleanField(default=False)

    def __str__(self):
        return self.nome

class CorProduto(Base):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Fabricante(Base):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class MemoriaProduto(Base):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class EstadoProduto(Base):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
