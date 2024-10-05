from django.db import models

class Produto(models.Model):
    codigo = models.CharField(max_length=20)
    nome = models.CharField(max_length=100)
    tipo = models.ForeignKey('TipoProduto', on_delete=models.PROTECT, related_name='tipo')
    fabricante = models.ForeignKey('Fabricante', on_delete=models.PROTECT, related_name='fabricante')
    cor = models.ForeignKey('CorProduto', on_delete=models.PROTECT, related_name='cor')
    memoria = models.ForeignKey('MemoriaProduto', on_delete=models.PROTECT, related_name='memoria')
    estado = models.ForeignKey('EstadoProduto', on_delete=models.PROTECT, related_name='estado')


class TipoProduto(models.Model):
    nome = models.CharField(max_length=100)
    numero_serial = models.BooleanField(default=False)

class CorProduto(models.Model):
    nome = models.CharField(max_length=100)

class Fabricante(models.Model):
    nome = models.CharField(max_length=100)

class MemoriaProduto(models.Model):
    nome = models.CharField(max_length=100)

class EstadoProduto(models.Model):
    nome = models.CharField(max_length=100)