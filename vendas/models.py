from django.db import models
from django.utils import timezone

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


class Caixa(Base):
    data_abertura = models.DateField(default=timezone.now)
    data_fechamento = models.DateField(null=True, blank=True)
    
    @property
    def saldo_total(self):
        return sum(venda.calcular_valor_total() for venda in self.vendas.filter(is_deleted=False).filter(loja=self.loja).filter(caixa=self))

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
        return self.vendas.filter(is_deleted=False).filter(loja=self.loja).filter(pagamentos__tipo_pagamento__nao_contabilizar=False).count()
    
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

class LancamentoCaixa(Base):
    tipo_lancamento_opcoes = (
        ('1', 'Crédito'),
        ('2', 'Débito'),
    )

    caixa = models.ForeignKey('vendas.Caixa', on_delete=models.PROTECT, related_name='lancamentos_caixa')
    motivo = models.CharField(max_length=100)
    tipo_lancamento = models.CharField(max_length=1, choices=tipo_lancamento_opcoes)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.tipo_lancamento} - R$ {self.valor}"
    
    class Meta:
        verbose_name_plural = 'Lancamentos Caixa'


class Loja(Base):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=14, null=True, blank=True)
    inscricao_estadual = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=200, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    meta_vendas_diaria = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    meta_vendas_mensal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_caixa_diaria = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    logo_loja = models.ImageField(upload_to='logos_lojas/', null=True, blank=True)
    mensagem_garantia = models.TextField(null=True, blank=True)
    contrato = models.JSONField(null=True, blank=True, default=dict)
    usuarios = models.ManyToManyField('accounts.User', related_name='lojas')
    gerentes = models.ManyToManyField('accounts.User', related_name='lojas_gerenciadas')

    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Lojas'

class Cliente(Base):
    nome = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    cpf = models.CharField(max_length=14)
    nascimento = models.DateField()
    rg = models.CharField(max_length=20, null=True, blank=True)
    cep = models.CharField(max_length=8, null=True, blank=True)
    endereco = models.CharField(max_length=200, null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    uf = models.CharField(max_length=2, null=True, blank=True)
    cliente_cred_facil = models.BooleanField(default=False)
    comprovantes = models.ForeignKey('vendas.ComprovantesCliente', on_delete=models.PROTECT, related_name='comprovantes_clientes', null=True, blank=True)
    contato_adicional = models.ForeignKey('vendas.ContatoAdicional', on_delete=models.PROTECT, related_name='contatos_adicionais', null=True, blank=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Clientes'

class ContatoAdicional(Base):
    nome_adicional = models.CharField(max_length=100, null=True, blank=True)
    contato = models.CharField(max_length=20, null=True, blank=True)
    endereco_adicional = models.CharField(max_length=200, null=True, blank=True)

class Endereco(Base):
    cep = models.CharField(max_length=8)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100)
    
    def __str__(self):
        return self.endereco
    
    class Meta:
        verbose_name_plural = 'Informacoes Clientes'

class ComprovantesCliente(Base):
    documento_identificacao_frente = models.ImageField(upload_to='comprovantes_clientes/%Y/%m/%d/', null=True, blank=True)
    documento_identificacao_verso = models.ImageField(upload_to='comprovantes_clientes/%Y/%m/%d/', null=True, blank=True)
    comprovante_residencia = models.ImageField(upload_to='comprovantes_clientes/%Y/%m/%d/', null=True, blank=True)
    consulta_serasa = models.ImageField(upload_to='comprovantes_clientes/%Y/%m/%d/', null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Comprovantes Clientes'


class Venda(Base):
    data_venda = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey('vendas.cliente', on_delete=models.PROTECT, related_name='vendas')
    vendedor = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='vendas_realizadas')
    tipo_venda = models.ForeignKey('vendas.TipoVenda', on_delete=models.PROTECT, related_name='vendas_tipo_venda')
    tipo_entrega = models.ForeignKey('vendas.TipoEntrega', on_delete=models.PROTECT, related_name='vendas_tipo_entrega')
    produtos = models.ManyToManyField('produtos.Produto', through='ProdutoVenda', related_name='vendas')
    caixa = models.ForeignKey('vendas.Caixa', on_delete=models.PROTECT, related_name='vendas')
    observacao = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    @property
    def pagamentos_valor_total(self):
        return sum(pagamento.valor for pagamento in self.pagamentos.all().filter(tipo_pagamento__nao_contabilizar=False))
    
    @property
    def pagamentos_valor_total_dinheiro(self):
        return sum(pagamento.valor for pagamento in self.pagamentos.all() if pagamento.tipo_pagamento.caixa)
    
    
    def calcular_valor_total(self):
        return sum(produto.calcular_valor_total() for produto in self.itens_venda.all())
    
    def __str__(self):
        return f"{self.cliente} - {self.data_venda.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name_plural = 'Vendas'
        permissions = (
            ('can_more_desconto', 'Pode dar mais desconto'),
        )

class ProdutoVenda(Base):
    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT, related_name='produto_vendas')
    imei = models.CharField(max_length=100, null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField()
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    venda = models.ForeignKey('vendas.Venda', on_delete=models.PROTECT, related_name='itens_venda')
    

    def calcular_valor_total(self):
        return (self.valor_unitario * self.quantidade) - self.valor_desconto
    
    def lucro(self):
        from estoque.models import ProdutoEntrada
        return (self.valor_unitario - ProdutoEntrada.objects.filter(produto=self.produto).last().custo_unitario) * self.quantidade
    
    def custo(self):
        from estoque.models import ProdutoEntrada
        return ProdutoEntrada.objects.filter(produto=self.produto).last().custo_unitario * self.quantidade
    
    def __str__(self):
        return f"{self.produto.nome} x {self.quantidade} (R$ {self.valor_unitario})"
    
    class Meta:
        verbose_name_plural = 'Produtos Vendas'
        

class Pagamento(Base):
    venda = models.ForeignKey('vendas.Venda', on_delete=models.PROTECT, related_name='pagamentos')
    tipo_pagamento = models.ForeignKey('vendas.TipoPagamento', on_delete=models.PROTECT, related_name='pagamentos_tipo')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    parcelas = models.PositiveIntegerField(default=1, null=True, blank=True)
    # valor_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    data_primeira_parcela = models.DateField()
    
    @property
    def valor_parcela(self):
        return self.valor / self.parcelas
    
    def __str__(self):
        return f"Pagamento de R$ {self.valor} via {self.tipo_pagamento.nome}"
    
    class Meta:
        verbose_name_plural = 'Pagamentos'
    

class TipoPagamento(Base):
    nome = models.CharField(max_length=100)
    caixa = models.BooleanField(default=False)
    parcelas = models.BooleanField(default=False)
    financeira = models.BooleanField(default=False)
    carne = models.BooleanField(default=False)
    nao_contabilizar = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nome
    
    class  Meta:
        verbose_name_plural = 'Tipos de Pagamentos'
        

class Parcela(Base):
    pagamento = models.ForeignKey('vendas.Pagamento', on_delete=models.PROTECT, related_name='parcelas_pagamento')
    numero_parcela = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    tipo_pagamento = models.ForeignKey('vendas.TipoPagamento', on_delete=models.PROTECT, related_name='parcelas_tipo_pagamento', null=True, blank=True)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    data_vencimento = models.DateField()
    pago = models.BooleanField(default=False)

    @property
    def valor_restante(self):
        valor_pago = self.valor_pago or 0
        desconto = self.desconto or 0
        return (self.valor - desconto) - valor_pago

    def __str__(self):
        return f"Parcela {self.numero_parcela} de {self.pagamento}"
        

class TipoEntrega(Base):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Tipos de Entrega'

class TipoVenda(Base):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Tipos de Vendas'
        