from django.db import models

class Loja(models.Model):
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

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    cpf = models.CharField(max_length=11)
    nascimento = models.DateField()
    rg = models.CharField(max_length=20)
    cliente_cred_facil = models.BooleanField(default=False)
    InformacoesCliente = models.ForeignKey('InformacoesCliente', on_delete=models.PROTECT, related_name='informacoes_cliente')
    ComprovantesCliente = models.ForeignKey('ComprovantesCliente', on_delete=models.PROTECT, related_name='comprovantes_cliente')

class InformacoesCliente(models.Model):
    cep = models.CharField(max_length=8)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100)

class ComprovantesCliente(models.Model):
    documento_identificacao_frente = models.ImageField(upload_to='comprovantes_clientes/', null=True, blank=True)
    documento_identificacao_verso = models.ImageField(upload_to='comprovantes_clientes/', null=True, blank=True)
    comprovante_residencia = models.ImageField(upload_to='comprovantes_clientes/', null=True, blank=True)
    consulta_serasa = models.ImageField(upload_to='comprovantes_clientes/', null=True, blank=True)

class Venda(models.Model):
    data_venda = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, related_name='cliente')
    vendedor = models.ForeignKey('Vendedor', on_delete=models.PROTECT, related_name='vendedor')
    tipo_venda = models.ForeignKey('TipoVenda', on_delete=models.PROTECT, related_name='tipo_venda')
    tipo_entrega = models.ForeignKey('TipoEntrega', on_delete=models.PROTECT, related_name='tipo_entrega')
    produtos = models.ManyToManyField('Produto', through='ProdutoVenda', related_name='produtos')

class Pagamento(models.Model):
    venda = models.ForeignKey('Venda', on_delete=models.PROTECT, related_name='pagamento')
    tipo_pagamento = models.ForeignKey('TipoPagamento', on_delete=models.PROTECT, related_name='tipo_pagamento')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    parcelas = models.IntegerField()
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    data_primeira_parcela = models.DateField()

class TipoPagamento(models.Model):
    nome = models.CharField(max_length=100)
    caixa = models.BooleanField(default=False)
    parcelas = models.BooleanField(default=False)
    financeira = models.BooleanField(default=False)

class TipoEntrega(models.Model):
    nome = models.CharField(max_length=100)

class TipoVenda(models.Model):
    nome = models.CharField(max_length=100)