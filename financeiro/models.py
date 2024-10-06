from django.db import models
from vendas.models import Base

class GastoFixo(Base):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Gastos Fixos'