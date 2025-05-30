# Generated by Django 4.2.16 on 2025-04-26 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0041_alter_venda_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='cliente_cred_facil',
        ),
        migrations.AlterField(
            model_name='cliente',
            name='bairro',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='cep',
            field=models.CharField(default='', max_length=8),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='cidade',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='comprovantes',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='comprovantes_clientes', to='vendas.comprovantescliente'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='endereco',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='rg',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='telefone',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='uf',
            field=models.CharField(default='', max_length=2),
            preserve_default=False,
        ),
    ]
