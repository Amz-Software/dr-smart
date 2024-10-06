from django.db import models
from django.utils import timezone

class Base(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True,editable=False)
    modificado_em = models.DateTimeField(auto_now=True,editable=False)
    criado_por = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='%(class)s_criadas',editable=False)
    modificado_por = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='%(class)s_modificadas',editable=False)
    
    def save(self, *args, user=None, **kwargs):
        if user:
            if not self.id: 
                self.criado_por = user
            self.modificado_por = user
        super().save(*args, **kwargs)
        
    class Meta:
        abstract = True


class Caixa(Base):
    data_abertura = models.DateField(auto_now_add=True)
    data_fechamento = models.DateField(null=True, blank=True)
    total_vendas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    @classmethod
    def caixa_aberto(cls, data):
        return cls.objects.filter(data_abertura=data, data_fechamento__isnull=True).exists()

    def __str__(self):
        return f"Caixa do dia {self.data_abertura}"

    class Meta:
        verbose_name_plural = 'Caixas'


class Loja(Base):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=14)
    endereco = models.CharField(max_length=200)
    inscricao_estadual = models.CharField(max_length=20)
    telefone = models.CharField(max_length=20)
    meta_vendas_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    meta_vendas_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    entrada_caixa_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    logo_loja = models.ImageField(upload_to='logos_lojas/', null=True, blank=True)
    mensagem_garantia = models.TextField(null=True, blank=True)
    contrato = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Lojas'

class Cliente(Base):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    cpf = models.CharField(max_length=11)
    nascimento = models.DateField()
    rg = models.CharField(max_length=20)
    cliente_cred_facil = models.BooleanField(default=False)
    Endereco = models.ForeignKey('vendas.Endereco', on_delete=models.PROTECT, related_name='informacoes_clientes')
    ComprovantesCliente = models.ForeignKey('vendas.ComprovantesCliente', on_delete=models.PROTECT, related_name='comprovantes_clientes')
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = 'Clientes'

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
    documento_identificacao_frente = models.ImageField(upload_to='comprovantes_clientes/', null=True, blank=True)
    documento_identificacao_verso = models.ImageField(upload_to='comprovantes_clientes/', null=True, blank=True)
    comprovante_residencia = models.ImageField(upload_to='comprovantes_clientes/', null=True, blank=True)
    consulta_serasa = models.ImageField(upload_to='comprovantes_clientes/', null=True, blank=True)
    
    def __str__(self):
        return self.documento_identificacao_frente
    
    class Meta:
        verbose_name_plural = 'Comprovantes Clientes'


class Venda(Base):
    data_venda = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey('vendas.Cliente', on_delete=models.PROTECT, related_name='vendas')
    vendedor = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='vendas_realizadas')
    tipo_venda = models.ForeignKey('vendas.TipoVenda', on_delete=models.PROTECT, related_name='vendas_tipo_venda')
    tipo_entrega = models.ForeignKey('vendas.TipoEntrega', on_delete=models.PROTECT, related_name='vendas_tipo_entrega')
    produtos = models.ManyToManyField('produtos.Produto', through='ProdutoVenda', related_name='vendas')
    caixa = models.ForeignKey('vendas.Caixa', on_delete=models.PROTECT, related_name='vendas')
    
    def calcular_valor_total(self):
        return sum(item.valor_unitario * item.quantidade for item in self.itens_venda.all())
    
    def __str__(self):
        return f"Venda {self.id} - {self.data_venda.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name_plural = 'Vendas'
        

class ProdutoVenda(Base):
    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT, related_name='produto_vendas')
    venda = models.ForeignKey('vendas.Venda', on_delete=models.PROTECT, related_name='itens_venda')
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.produto.nome} x {self.quantidade} (R$ {self.valor_unitario})"
    
    class Meta:
        verbose_name_plural = 'Produtos Vendas'
        

class Pagamento(Base):
    venda = models.ForeignKey('vendas.Venda', on_delete=models.PROTECT, related_name='pagamentos')
    tipo_pagamento = models.ForeignKey('vendas.TipoPagamento', on_delete=models.PROTECT, related_name='pagamentos_tipo')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    parcelas = models.PositiveIntegerField(default=1)
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    data_primeira_parcela = models.DateField()
    
    def save(self, *args, **kwargs):
        if self.parcelas > 0:
            self.valor_parcela = self.valor / self.parcelas
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Pagamento de R$ {self.valor} via {self.tipo_pagamento.nome}"
    
    class Meta:
        verbose_name_plural = 'Pagamentos'
    

class TipoPagamento(Base):
    nome = models.CharField(max_length=100)
    caixa = models.BooleanField(default=False)
    parcelas = models.BooleanField(default=False)
    financeira = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nome
    
    class  Meta:
        verbose_name_plural = 'Tipos de Pagamentos'
        

class Parcela(Base):
    pagamento = models.ForeignKey('vendas.Pagamento', on_delete=models.PROTECT, related_name='parcelas_pagamento')
    numero_parcela = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    pago = models.BooleanField(default=False)

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
        