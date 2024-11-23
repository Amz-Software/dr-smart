from django.db import models
from vendas.models import Base

class GastoFixo(Base):
    nome = models.CharField(max_length=100)
    loja = models.ForeignKey('vendas.Loja', on_delete=models.PROTECT, related_name='gastos_fixos')
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Gastos Fixos'
        

class Funcionario(Base):
    nome = models.CharField(max_length=100)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    loja = models.ForeignKey('vendas.Loja', on_delete=models.PROTECT, related_name='funcionarios')
    user = models.OneToOneField('auth.User', on_delete=models.PROTECT, related_name='funcionario')
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Funcionários'


