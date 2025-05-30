# Generated by Django 4.2.16 on 2024-12-01 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0011_produtovenda_imei_produtovenda_valor_desconto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loja',
            name='cnpj',
            field=models.CharField(blank=True, max_length=14, null=True),
        ),
        migrations.AlterField(
            model_name='loja',
            name='endereco',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='loja',
            name='entrada_caixa_diaria',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='loja',
            name='inscricao_estadual',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='loja',
            name='meta_vendas_diaria',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='loja',
            name='meta_vendas_mensal',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='loja',
            name='telefone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
