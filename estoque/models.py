from django.db import models

class EntradaEstoque(models.Model):
    fornecedor = models.ForeignKey('Fornecedor', on_delete=models.PROTECT, related_name='fornecedor')
    data_entrada = models.DateField()
    numero_nota = models.CharField(max_length=20)
    produto = models.ForeignKey('Produto', on_delete=models.PROTECT, related_name='produto')
    imei = models.CharField(max_length=20)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    venda_unitaria = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.IntegerField()
    custo_total = models.DecimalField(max_digits=10, decimal_places=2)
    venda_total = models.DecimalField(max_digits=10, decimal_places=2)