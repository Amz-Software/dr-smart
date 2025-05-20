from django.db import models
from django.utils import timezone
from vendas.models import Cliente

class Base(models.Model):
    loja = models.ForeignKey('vendas.Loja', on_delete=models.PROTECT, related_name='%(class)s_loja', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True,editable=False)
    modificado_em = models.DateTimeField(auto_now=True,editable=False)
    criado_por = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='%(class)s_criadas',editable=False, null=True, blank=True)
    modificado_por = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='%(class)s_modificadas',editable=False, null=True, blank=True)
    
    def save(self, *args, user=None, **kwargs):
        if user:
            if not self.pk: 
                self.criado_por = user
            self.modificado_por = user
        super().save(*args, **kwargs)
        
    class Meta:
        abstract = True

# Create your models here.
class CaixaAssistencia(Base):
    data_abertura = models.DateField(default=timezone.now)
    data_fechamento = models.DateField(null=True, blank=True)
    
    @property
    def saldo_total(self):
        return sum(venda.pagamentos_valor_total for venda in self.vendas.filter(is_deleted=False).filter(loja=self.loja).filter(caixa=self))
    
    @property
    def saldo_total_dinheiro(self):
        total = sum(venda.pagamentos_valor_total_dinheiro for venda in self.vendas.filter(is_deleted=False, pagamentos__tipo_pagamento__caixa=True).filter(loja=self.loja).filter(caixa=self))
        return total if total else 0
    
    def saldo_final(self):
        return (self.saldo_total_dinheiro + self.entradas) - self.saidas

    @property
    def saidas(self):
        return sum(lancamento.valor for lancamento in self.lancamentos_caixa.filter(tipo_lancamento='2'))
    
    @property
    def entradas(self):
        return sum(lancamento.valor for lancamento in self.lancamentos_caixa.filter(tipo_lancamento='1'))
    
    @property
    def quantidade_vendas(self):
        return self.vendas.filter(is_deleted=False).filter(loja=self.loja).filter(caixa=self).count()
    
    @property
    def caixa_fechado(self):
        if self.data_fechamento:
            return True
        return False
        
    
    @classmethod
    def caixa_aberto(cls, data, loja):
        return cls.objects.filter(data_abertura=data, data_fechamento__isnull=True, loja=loja).exists()

    def __str__(self):
        return f"Caixa do dia {self.data_abertura} - {self.loja}"

    class Meta:
        verbose_name_plural = 'Caixas'
        permissions = [('view_assistencia', 'Pode visualizar assistência')]

class PecaOrdemServico(models.Model):
    ordem_servico = models.ForeignKey('assistencia.OrdemServico', on_delete=models.CASCADE, related_name='pecas_ordem_servico')
    produto = models.ForeignKey('produtos.Produto', on_delete=models.CASCADE, related_name='pecas_produto')
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade}"
    
    class Meta:
        verbose_name_plural = 'Peças por Ordem de Serviço'
        permissions = [('view_assistencia', 'Pode visualizar assistência')]

class OrdemServico(Base):
    STATUS_CHOICES = [
        ('EM MONTAGEM', 'Em Montagem'),
        ('EM TESTE', 'Em Teste'),
        ('SEM CONSERTO', 'Sem Conserto'),
        ('FINALIZADA', 'Finalizada'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ordem_servico_cliente', null=True, blank=True)
    aparelho = models.CharField(max_length=100)
    defeito_relato = models.TextField()
    pecas = models.ManyToManyField('produtos.Produto', through='PecaOrdemServico', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EM MONTAGEM')
    mao_de_obra = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    valor_servico = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    data_finalizacao = models.DateTimeField(null=True, blank=True)
    loja = models.ForeignKey('vendas.Loja', on_delete=models.PROTECT, related_name='ordem_servico_loja', null=True, blank=True)

    def __str__(self):
        return f'OS #{self.id} - {self.aparelho} - {self.loja}'

    class Meta:
        verbose_name_plural = 'Ordens de Serviço'
        permissions = [('view_assistencia', 'Pode visualizar assistência')]


class PagamentoAssistencia(Base):
    ordem_servico = models.ForeignKey(
        'assistencia.OrdemServico', on_delete=models.PROTECT, related_name='pagamentos'
    )
    tipo_pagamento = models.ForeignKey(
        'vendas.TipoPagamento', on_delete=models.PROTECT, related_name='pagamentos_assistencia_tipo'
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    parcelas = models.PositiveIntegerField(default=1, null=True, blank=True)
    data_primeira_parcela = models.DateField()

    @property
    def valor_parcela(self):
        return self.valor / self.parcelas

    def __str__(self):
        return f"Pagamento de R$ {self.valor} via {self.tipo_pagamento.nome}"

    class Meta:
        verbose_name_plural = 'Pagamentos Assistência'

class ParcelaAssistencia(Base):
    pagamento = models.ForeignKey(
        'assistencia.PagamentoAssistencia', on_delete=models.PROTECT,
        related_name='parcelas_pagamento_assistencia'
    )
    numero_parcela = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2,
                                     null=True, blank=True, default=0)
    tipo_pagamento = models.ForeignKey(
        'vendas.TipoPagamento', on_delete=models.PROTECT,
        related_name='parcelas_assistencia_tipo', null=True, blank=True
    )
    desconto = models.DecimalField(max_digits=10, decimal_places=2,
                                  null=True, blank=True, default=0)
    data_vencimento = models.DateField()
    pago = models.BooleanField(default=False)

    @property
    def valor_restante(self):
        valor_pago = self.valor_pago or 0
        desconto = self.desconto or 0
        return (self.valor - desconto) - valor_pago

    def __str__(self):
        return f"Parcela {self.numero_parcela} de {self.pagamento}"

    class Meta:
        verbose_name_plural = 'Parcelas Assistência'
